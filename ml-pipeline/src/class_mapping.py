import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPLITS_DIR = PROJECT_ROOT / "data" / "splits" / "v2"
OUTPUT_PATH = PROJECT_ROOT / "ml-pipeline" / "src" / "class_mapping.json"


def create_class_mapping():
    labels = set()

    for split in ["train", "val", "test"]:
        csv_path = SPLITS_DIR / f"{split}.csv"
        frame = pd.read_csv(csv_path, encoding="utf-8-sig")
        labels.update(frame["label"].dropna().tolist())

    class_names = sorted(labels)

    if len(class_names) != 57:
        raise ValueError(
            f"Expected 57 classes, found {len(class_names)}"
        )

    class_to_idx = {
        name: index
        for index, name in enumerate(class_names)
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            class_to_idx,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"SUCCESS: Saved {len(class_to_idx)} classes.")
    print(f"File: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_class_mapping()
