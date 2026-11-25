#!/usr/bin/env python
"""Read-only audit for an image-folder dataset. Never edits or deletes source images."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline_config import load_config, project_path
from PIL import Image, UnidentifiedImageError

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    dataset_config = load_config()["dataset"]
    parser = argparse.ArgumentParser(
        description="Audit image files without modifying them."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=project_path(dataset_config["data_dir"]),
        help="Root folder containing the extracted dataset",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_path(dataset_config["audit_output_dir"]),
        help="Folder where audit reports will be written",
    )
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not data_dir.exists() or not data_dir.is_dir():
        parser.error(
            f"Dataset folder does not exist or is not a directory: {data_dir}"
        )

    # Keep generated reports outside the original dataset.
    try:
        output_dir.relative_to(data_dir)
        parser.error("Output folder must be outside the original dataset folder.")
    except ValueError:
        pass
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        path
        for path in data_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )
    rows = []
    bad = []
    hashes = defaultdict(list)
    sizes = Counter()
    extensions = Counter()

    for path in files:
        relative_path = path.relative_to(data_dir).as_posix()
        # Nested folder layouts may make the immediate parent a misleading label.
        parts = Path(relative_path).parts
        label = parts[-2] if len(parts) >= 2 else "(root-level / unknown)"

        try:
            with Image.open(path) as image:
                image.verify()
            # verify() invalidates the image object, so reopen it to read metadata.
            with Image.open(path) as image:
                width, height = image.size
                mode = image.mode
                image_format = image.format or path.suffix.lower().lstrip(".")

            sizes[(width, height)] += 1
            digest = sha256_file(path)
            hashes[digest].append(relative_path)
            extensions[path.suffix.lower()] += 1
            rows.append(
                {
                    "relative_path": relative_path,
                    "inferred_parent_label": label,
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "format": image_format,
                    "sha256": digest,
                    "status": "ok",
                }
            )
        except (UnidentifiedImageError, OSError, ValueError) as error:
            bad.append({"relative_path": relative_path, "error": str(error)})
            rows.append(
                {
                    "relative_path": relative_path,
                    "inferred_parent_label": label,
                    "width": "",
                    "height": "",
                    "mode": "",
                    "format": "",
                    "sha256": "",
                    "status": "unreadable",
                }
            )

    counts = Counter(
        row["inferred_parent_label"] for row in rows if row["status"] == "ok"
    )
    # Hashes identify byte-for-byte copies, not visually similar images.
    duplicates = {
        digest: paths for digest, paths in hashes.items() if len(paths) > 1
    }

    with (output_dir / "images.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "relative_path",
                "inferred_parent_label",
                "width",
                "height",
                "mode",
                "format",
                "sha256",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    with (output_dir / "class_counts.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["inferred_parent_label", "readable_image_count"])
        writer.writerows(sorted(counts.items(), key=lambda item: item[0].casefold()))

    with (output_dir / "unreadable_images.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=["relative_path", "error"])
        writer.writeheader()
        writer.writerows(bad)

    with (output_dir / "exact_duplicates.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(duplicates, file, indent=2, ensure_ascii=False)

    summary = {
        "dataset_root": str(data_dir),
        "image_files_found_by_extension": len(files),
        "readable_images": sum(row["status"] == "ok" for row in rows),
        "unreadable_images": len(bad),
        "inferred_parent_label_count": len(counts),
        "dimensions_of_readable_images": {
            f"{width}x{height}": count
            for (width, height), count in sorted(sizes.items())
        },
        "extensions": dict(extensions),
        "exact_duplicate_groups": len(duplicates),
        "class_label_inference_warning": (
            "Labels are inferred from each image's immediate parent directory only. "
            "Check nested folders manually before trusting class counts."
        ),
        "signer_identity": (
            "Not inferred by this script; inspect source metadata and folder names "
            "manually."
        ),
        "source_modified": False,
    }
    with (output_dir / "dataset-audit.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    lines = [
        "# Dataset Audit Report",
        "",
        (
            "> Automatically generated. Review class labels and folder structure "
            "manually before training."
        ),
        "",
        "## Summary",
        f"- Image files found: **{len(files)}**",
        f"- Readable images: **{summary['readable_images']}**",
        f"- Unreadable images: **{len(bad)}**",
        f"- Inferred parent-folder labels: **{len(counts)}**",
        f"- Exact duplicate-content groups: **{len(duplicates)}**",
        "- Source files modified: **No**",
        "",
        "## Readable image dimensions",
    ]
    lines += [
        f"- `{width}x{height}`: {count}"
        for (width, height), count in sorted(sizes.items())
    ] or ["- No readable images found."]
    lines += [
        "",
        "## Inferred images per parent folder",
        "",
        "| Parent folder (possible label) | Readable images |",
        "|---|---:|",
    ]
    lines += [
        f"| `{label}` | {count} |"
        for label, count in sorted(counts.items(), key=lambda item: item[0].casefold())
    ]
    lines += [
        "",
        "## Files created",
        "- `images.csv`: per-image metadata and hash",
        "- `class_counts.csv`: readable image counts by inferred parent folder",
        "- `unreadable_images.csv`: files Pillow could not read",
        (
            "- `exact_duplicates.json`: identical file-content groups "
            "(not perceptual duplicates)"
        ),
        "- `dataset-audit.json`: machine-readable summary",
        "",
        "## Important limitations",
        (
            "- Class names are inferred from each image's immediate parent folder. "
            "Nested directory layouts can make these labels wrong."
        ),
        (
            "- Hash matching finds byte-for-byte identical files, not visually "
            "identical images saved with different compression."
        ),
        (
            "- Signer identity, label correctness, and semantic validity require "
            "manual inspection/source metadata."
        ),
        (
            "- This report is an audit only; it does not clean, resize, move, "
            "or delete images."
        ),
        "",
    ]
    # Write a readable report alongside the machine-readable CSV and JSON files.
    (output_dir / "dataset-audit.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"Audit complete. Reports saved to: {output_dir}")
    print(
        f"Found {len(files)} image files; "
        f"{summary['readable_images']} readable; {len(bad)} unreadable."
    )
    print(
        "Open dataset-audit.md and class_counts.csv, "
        "then review the folder-label inference."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
