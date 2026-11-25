#!/usr/bin/env python
"""Create reproducible train/validation/test CSV manifests without changing source images."""

import argparse
import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline_config import load_config, project_path
from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    config = load_config()
    dataset_config = config["dataset"]
    split_config = dataset_config["splits"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", type=Path, default=project_path(dataset_config["data_dir"])
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_path(split_config["output_dir"]),
    )
    parser.add_argument("--seed", type=int, default=split_config["seed"])
    parser.add_argument("--train", type=float, default=split_config["train_ratio"])
    parser.add_argument("--val", type=float, default=split_config["validation_ratio"])
    parser.add_argument("--test", type=float, default=split_config["test_ratio"])
    args = parser.parse_args()

    if (
        any(ratio < 0 for ratio in (args.train, args.val, args.test))
        or abs(args.train + args.val + args.test - 1) > 1e-8
    ):
        parser.error("train, val, and test ratios must be nonnegative and sum to 1")

    data = args.data_dir.resolve()
    output = args.output_dir.resolve()
    if not data.is_dir():
        parser.error(f"Dataset folder not found: {data}")

    # Keep generated manifests and reports outside the original image dataset.
    try:
        output.relative_to(data)
        parser.error("Output must be outside the original dataset folder.")
    except ValueError:
        pass

    files = sorted(
        path
        for path in data.rglob("*")
        if path.is_file() and path.suffix.lower() in EXTS
    )
    groups = defaultdict(list)
    skipped = []
    class_dirs = set()

    for path in files:
        relative_path = path.relative_to(data).as_posix()
        parts = Path(relative_path).parts
        if len(parts) < 2:
            skipped.append(
                {
                    "path": relative_path,
                    "reason": "root-level image has no verified class label; excluded",
                }
            )
            continue

        if (
            len(parts) < 4
            or parts[0] != "Data"
            or parts[1]
            not in {
                "Demandes",
                "Destinations",
                "Famille",
                "Jours",
                "Transport",
            }
        ):
            skipped.append(
                {
                    "path": relative_path,
                    "reason": (
                        "path does not match "
                        "Data/<category>/<sign-label>/<image>"
                    ),
                }
            )
            continue

        category = parts[1]
        label = parts[2]

        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
        except Exception as error:
            skipped.append(
                {"path": relative_path, "reason": f"unreadable: {error}"}
            )
            continue

        class_dirs.add(label)
        digest = sha256(path)
        # Group by label and exact content hash so duplicate files stay together.
        groups[(label, digest)].append(
            {
                "relative_path": relative_path,
                "label": label,
                "category": category,
                "sha256": digest,
                "width": width,
                "height": height,
            }
        )

    if not groups:
        parser.error("No eligible images found. Check the folder layout.")

    per_class = defaultdict(list)
    for (label, digest), rows in groups.items():
        per_class[label].append((digest, rows))

    rng = random.Random(args.seed)
    splits = {"train": [], "val": [], "test": []}
    summary = {}

    for label in sorted(per_class, key=str.casefold):
        groups_for_class = per_class[label]
        rng.shuffle(groups_for_class)
        count = len(groups_for_class)

        if count >= 3:
            train_count = max(1, round(count * args.train))
            val_count = max(1, round(count * args.val))
            test_count = count - train_count - val_count

            # Give each split a group when possible without exceeding the class total.
            while test_count < 1:
                if train_count > 1:
                    train_count -= 1
                elif val_count > 1:
                    val_count -= 1
                else:
                    break
                test_count = count - train_count - val_count

            while train_count + val_count + test_count > count:
                if train_count > 1:
                    train_count -= 1
                elif val_count > 1:
                    val_count -= 1
                else:
                    test_count -= 1

            while train_count + val_count + test_count < count:
                train_count += 1
        else:
            train_count, val_count, test_count = count, 0, 0

        chunks = {
            "train": groups_for_class[:train_count],
            "val": groups_for_class[train_count : train_count + val_count],
            "test": groups_for_class[train_count + val_count :],
        }
        for split, chunk in chunks.items():
            for _, rows in chunk:
                for row in rows:
                    splits[split].append({**row, "split": split})

        summary[label] = {
            "unique_hash_groups": count,
            **{
                split: sum(len(rows) for _, rows in chunks[split])
                for split in chunks
            },
        }

    output.mkdir(parents=True, exist_ok=True)
    fields = [
        "relative_path",
        "label",
        "category",
        "sha256",
        "width",
        "height",
        "split",
    ]
    for split, rows in splits.items():
        rows.sort(
            key=lambda row: (
                row["label"].casefold(),
                row["relative_path"].casefold(),
            )
        )
        with (output / f"{split}.csv").open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    hash_splits = defaultdict(set)
    for split, rows in splits.items():
        for row in rows:
            hash_splits[row["sha256"]].add(split)
    leaks = {digest: list(split_names) for digest, split_names in hash_splits.items()
             if len(split_names) > 1}

    report = {
        "seed": args.seed,
        "source_directory": str(data),
        "counts": {split: len(rows) for split, rows in splits.items()},
        "eligible_images": sum(map(len, splits.values())),
        "class_count": len(summary),
        "excluded_or_unreadable": skipped,
        "duplicate_hash_leaks": len(leaks),
        "classes": summary,
        "warnings": [
            (
                "Class labels are inferred from the first folder below data-dir; "
                "verify this matches the official dataset layout."
            ),
            "Root-level images are excluded because their class label is unverified.",
            (
                "Identical file contents are kept in the same split; visually "
                "identical re-encodings are not detected."
            ),
            "Signer IDs are unavailable, so this is not signer-independent evaluation.",
            (
                "Classes with fewer than three unique hash groups cannot be "
                "represented in all three splits."
            ),
        ],
    }
    (output / "split-summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "# Split Generation Report",
        "",
        f"- Eligible images: **{report['eligible_images']}**",
        f"- Classes: **{report['class_count']}**",
        f"- Train: **{report['counts']['train']}**",
        f"- Validation: **{report['counts']['val']}**",
        f"- Test: **{report['counts']['test']}**",
        f"- Exact duplicate hash leaks: **{len(leaks)}**",
        "",
        "## Per-class counts",
        "",
        "| Class | Unique hash groups | Train | Validation | Test |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, counts in sorted(summary.items(), key=lambda item: item[0].casefold()):
        lines.append(
            f"| `{label}` | {counts['unique_hash_groups']} | "
            f"{counts['train']} | {counts['val']} | {counts['test']} |"
        )

    lines += ["", "## Warnings"] + [
        "- " + warning for warning in report["warnings"]
    ]
    if skipped:
        lines += ["", "## Excluded files / issues"] + [
            f"- `{item['path']}`: {item['reason']}" for item in skipped
        ]
    if leaks:
        lines += [
            "",
            (
                "**ERROR:** identical hashes occur across splits; do not train on "
                "these manifests."
            ),
        ]

    (output / "split-summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(f"Created manifests in {output}")
    print(
        f"Eligible images: {report['eligible_images']} | "
        f"classes: {report['class_count']} | "
        f"train/val/test: {report['counts']['train']}/"
        f"{report['counts']['val']}/{report['counts']['test']}"
    )
    print(f"Exact duplicate hashes across splits: {len(leaks)}")
    print("Review split-summary.md before training.")
    return 2 if leaks else 0


if __name__ == "__main__":
    raise SystemExit(main())
