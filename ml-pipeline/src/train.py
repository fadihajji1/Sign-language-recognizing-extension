"""Train the ResNet18 TSL isolated-sign baseline."""

import argparse
import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.optim import AdamW
import PIL
import torchvision

from pipeline_config import load_config, project_path
from tsl_data import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    SPLITS_DIR,
    create_dataloaders,
)
from models import build_model


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def run_epoch(model, loader, loss_fn, device, optimizer=None):
    training = optimizer is not None
    model.train(training)
    loss_sum = 0.0
    correct = 0
    count = 0

    with torch.set_grad_enabled(training):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = loss_fn(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
            batch_size = labels.size(0)
            loss_sum += loss.item() * batch_size
            correct += (logits.argmax(dim=1) == labels).sum().item()
            count += batch_size

    return {"loss": loss_sum / count, "accuracy": correct / count}


def main():
    training_config = load_config()["training"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--architecture",
        choices=("resnet18", "mobilenet_v3_small"),
        default=training_config["architecture"],
    )
    parser.add_argument("--epochs", type=int, default=training_config["epochs"])
    parser.add_argument(
        "--batch-size", type=int, default=training_config["batch_size"]
    )
    parser.add_argument(
        "--learning-rate", type=float, default=training_config["learning_rate"]
    )
    parser.add_argument(
        "--weight-decay", type=float, default=training_config["weight_decay"]
    )
    parser.add_argument("--seed", type=int, default=training_config["seed"])
    parser.add_argument(
        "--num-workers", type=int, default=training_config["num_workers"]
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_path(training_config["output_dir"]),
    )
    parser.add_argument(
        "--device",
        choices=("cpu", "cuda"),
        default=training_config["device"],
    )
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("--epochs must be at least 1")

    seed_everything(args.seed)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA was requested but is unavailable")

    loaders, class_to_idx = create_dataloaders(args.batch_size, args.num_workers)
    model = build_model(args.architecture, len(class_to_idx)).to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "experiment": output_dir.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "architecture": args.architecture,
        "pretrained_weights": None,
        "initialization": "random",
        "classes": len(class_to_idx),
        "epochs_requested": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "seed": args.seed,
        "device": str(device),
        "image_size": IMAGE_SIZE,
        "normalization": {"mean": IMAGENET_MEAN, "std": IMAGENET_STD},
        "splits": str(SPLITS_DIR),
        "python": sys.version,
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "pillow": PIL.__version__,
    }
    (output_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (output_dir / "class_mapping.json").write_text(
        json.dumps(class_to_idx, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    best_accuracy = -1.0
    with (output_dir / "training_log.csv").open("w", newline="", encoding="utf-8") as log_file:
        writer = csv.DictWriter(log_file, fieldnames=[
            "epoch", "train_loss", "train_accuracy", "val_loss", "val_accuracy"
        ])
        writer.writeheader()
        for epoch in range(1, args.epochs + 1):
            train_metrics = run_epoch(model, loaders["train"], loss_fn, device, optimizer)
            val_metrics = run_epoch(model, loaders["val"], loss_fn, device)
            row = {
                "epoch": epoch,
                "train_loss": train_metrics["loss"],
                "train_accuracy": train_metrics["accuracy"],
                "val_loss": val_metrics["loss"],
                "val_accuracy": val_metrics["accuracy"],
            }
            writer.writerow(row)
            log_file.flush()
            print(
                f"Epoch {epoch}/{args.epochs} | "
                f"train loss {row['train_loss']:.4f}, acc {row['train_accuracy']:.4f} | "
                f"val loss {row['val_loss']:.4f}, acc {row['val_accuracy']:.4f}",
                flush=True,
            )
            if val_metrics["accuracy"] > best_accuracy:
                best_accuracy = val_metrics["accuracy"]
                torch.save({
                    "model_state_dict": model.state_dict(),
                    "class_to_idx": class_to_idx,
                    "epoch": epoch,
                    "val_accuracy": best_accuracy,
                    "config": config,
                }, output_dir / "best_model.pt")

    print(f"Best validation accuracy: {best_accuracy:.4f}")
    print(f"Artifacts: {output_dir}")


if __name__ == "__main__":
    main()
