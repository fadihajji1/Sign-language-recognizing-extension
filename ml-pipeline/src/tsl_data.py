
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# Project paths, relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "original" / "w7ch"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits" / "v2"

IMAGE_SIZE = 224

# ImageNet normalization is a common baseline for ResNet models.
# We will keep these settings consistent during training and inference.
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def get_transforms(training=False):
    """Create image transformations without modifying source files."""

    operations = []

    # Conservative augmentation, training split only.
    # No horizontal flips because mirroring may change a sign's meaning.
    if training:
        operations.extend([
            transforms.RandomAffine(
                degrees=5,
                translate=(0.03, 0.03),
            ),
            transforms.ColorJitter(
                brightness=0.10,
                contrast=0.10,
            ),
        ])

    operations.extend([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])

    return transforms.Compose(operations)


class TSLImageDataset(Dataset):
    """Load TSL images and their numeric class labels from a CSV manifest."""

    def __init__(self, csv_path, data_dir, class_to_idx, training=False):
        self.csv_path = Path(csv_path)
        self.data_dir = Path(data_dir)
        self.class_to_idx = class_to_idx
        self.transform = get_transforms(training=training)

        if not self.csv_path.is_file():
            raise FileNotFoundError(
                f"Manifest not found: {self.csv_path}"
            )

        self.records = pd.read_csv(self.csv_path, encoding="utf-8-sig")

        required_columns = {"relative_path", "label"}
        missing_columns = required_columns - set(self.records.columns)

        if missing_columns:
            raise ValueError(
                f"{self.csv_path.name} is missing columns: "
                f"{sorted(missing_columns)}"
            )

        if self.records.empty:
            raise ValueError(f"No images listed in {self.csv_path}")

        if self.records["label"].isna().any():
            raise ValueError(
                f"Missing class labels in {self.csv_path.name}"
            )

        unknown_labels = set(self.records["label"]) - set(class_to_idx)
        if unknown_labels:
            raise ValueError(
                f"Unknown labels in {self.csv_path.name}: "
                f"{sorted(unknown_labels)}"
            )

        # Check paths before training starts.
        missing_paths = []
        for relative_path in self.records["relative_path"]:
            image_path = self.data_dir / str(relative_path)
            if not image_path.is_file():
                missing_paths.append(str(image_path))
                if len(missing_paths) >= 10:
                    break

        if missing_paths:
            raise FileNotFoundError(
                "Some manifest image paths do not exist. Examples: "
                + "; ".join(missing_paths)
            )

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        row = self.records.iloc[index]
        image_path = self.data_dir / str(row["relative_path"])
        label_name = row["label"]

        # The image is opened read-only and converted in memory.
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image_tensor = self.transform(image)

        label_id = self.class_to_idx[label_name]

        return image_tensor, torch.tensor(label_id, dtype=torch.long)


def create_dataloaders(batch_size=32, num_workers=0):
    """Build training, validation, and test DataLoaders."""

    csv_paths = {
        "train": SPLITS_DIR / "train.csv",
        "val": SPLITS_DIR / "val.csv",
        "test": SPLITS_DIR / "test.csv",
    }

    # Derive one stable class mapping from all three manifests.
    # The same mapping is then used for every split.
    all_labels = set()

    for csv_path in csv_paths.values():
        if not csv_path.is_file():
            raise FileNotFoundError(
                f"Split CSV not found: {csv_path}"
            )

        frame = pd.read_csv(csv_path, encoding="utf-8-sig")

        if "label" not in frame.columns:
            raise ValueError(f"No 'label' column in {csv_path.name}")

        all_labels.update(frame["label"].dropna().tolist())

    class_names = sorted(all_labels)
    class_to_idx = {
        class_name: index
        for index, class_name in enumerate(class_names)
    }

    if len(class_to_idx) != 57:
        raise ValueError(
            f"Expected 57 classes, found {len(class_to_idx)}. "
            "Check the split CSV files."
        )

    datasets = {
        "train": TSLImageDataset(
            csv_paths["train"], DATA_DIR, class_to_idx, training=True
        ),
        "val": TSLImageDataset(
            csv_paths["val"], DATA_DIR, class_to_idx, training=False
        ),
        "test": TSLImageDataset(
            csv_paths["test"], DATA_DIR, class_to_idx, training=False
        ),
    }

    loaders = {
        "train": DataLoader(
            datasets["train"],
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
        ),
        "val": DataLoader(
            datasets["val"],
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
        ),
        "test": DataLoader(
            datasets["test"],
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
        ),
    }

    return loaders, class_to_idx


if __name__ == "__main__":
    print("Project root:", PROJECT_ROOT)
    print("Dataset directory:", DATA_DIR)
    print("Split directory:", SPLITS_DIR)

    loaders, class_to_idx = create_dataloaders(batch_size=8)

    print("\nClass count:", len(class_to_idx))
    print("Example class IDs:")
    for name, index in list(class_to_idx.items())[:10]:
        print(f"  {name}: {index}")

    print("\nSplit sizes:")
    for split_name, loader in loaders.items():
        print(f"  {split_name}: {len(loader.dataset)} images")

    # Load one batch to verify shapes and label values.
    images, labels = next(iter(loaders["train"]))

    print("\nFirst training batch:")
    print("  Image tensor shape:", tuple(images.shape))
    print("  Label tensor shape:", tuple(labels.shape))
    print("  Image tensor dtype:", images.dtype)
    print("  Label tensor dtype:", labels.dtype)
    print("  Label IDs in this batch:", labels.tolist())
    print("  All image values finite:", bool(torch.isfinite(images).all()))

    assert images.shape == (8, 3, IMAGE_SIZE, IMAGE_SIZE)
    assert labels.shape == (8,)
    assert labels.min().item() >= 0
    assert labels.max().item() < len(class_to_idx)
    assert torch.isfinite(images).all()

    print("\nSUCCESS: The TSL data pipeline passed its basic checks.")
