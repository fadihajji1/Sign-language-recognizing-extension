"""Evaluate a saved ResNet18 checkpoint on the held-out test split."""

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import torch
from tsl_data import create_dataloaders
from models import build_model


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT = PROJECT_ROOT / "experiments" / "resnet18-baseline-v1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-dir", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    args = parser.parse_args()
    experiment_dir = args.experiment_dir.resolve()
    checkpoint_path = experiment_dir / "best_model.pt"
    if not checkpoint_path.is_file():
        parser.error(f"Checkpoint not found: {checkpoint_path}")

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA was requested but is unavailable")
    loaders, class_to_idx = create_dataloaders(args.batch_size, args.num_workers)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    saved_mapping = checkpoint["class_to_idx"]
    if saved_mapping != class_to_idx:
        raise ValueError("Checkpoint class mapping does not match the current v2 splits")

    architecture = checkpoint["config"]["architecture"]
    model = build_model(architecture, len(class_to_idx))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device).eval()
    idx_to_class = {index: name for name, index in class_to_idx.items()}
    class_names = [idx_to_class[index] for index in range(len(idx_to_class))]
    true_ids, predicted_ids, confidences, latencies = [], [], [], []
    with torch.inference_mode():
        for images, labels in loaders["test"]:
            images = images.to(device)
            if device.type == "cuda":
                torch.cuda.synchronize()
            start = time.perf_counter()
            logits = model(images)
            if device.type == "cuda":
                torch.cuda.synchronize()
            elapsed = time.perf_counter() - start
            probs = torch.softmax(logits, dim=1)
            confidence, prediction = probs.max(dim=1)
            latencies.extend([elapsed / len(labels)] * len(labels))
            true_ids.extend(labels.tolist())
            predicted_ids.extend(prediction.cpu().tolist())
            confidences.extend(confidence.cpu().tolist())

    matrix = np.zeros((len(class_names), len(class_names)), dtype=np.int64)
    for truth, prediction in zip(true_ids, predicted_ids):
        matrix[truth, prediction] += 1
    per_class = {}
    for index, class_name in enumerate(class_names):
        tp = int(matrix[index, index])
        support = int(matrix[index, :].sum())
        predicted_count = int(matrix[:, index].sum())
        class_precision = tp / predicted_count if predicted_count else 0.0
        class_recall = tp / support if support else 0.0
        class_f1 = (
            2 * class_precision * class_recall / (class_precision + class_recall)
            if class_precision + class_recall else 0.0
        )
        per_class[class_name] = {
            "precision": class_precision,
            "recall": class_recall,
            "f1": class_f1,
            "support": support,
        }
    accuracy = float(np.trace(matrix) / len(true_ids))
    precision = float(np.mean([item["precision"] for item in per_class.values()]))
    recall = float(np.mean([item["recall"] for item in per_class.values()]))
    macro_f1 = float(np.mean([item["f1"] for item in per_class.values()]))
    metrics = {
        "checkpoint": str(checkpoint_path),
        "checkpoint_epoch": checkpoint["epoch"],
        "test_images": len(true_ids),
        "accuracy": accuracy,
        "macro_precision": precision,
        "macro_recall": recall,
        "macro_f1": macro_f1,
        "mean_model_latency_ms_per_image": float(np.mean(latencies) * 1000),
        "p50_model_latency_ms_per_image": float(np.percentile(latencies, 50) * 1000),
        "p95_model_latency_ms_per_image": float(np.percentile(latencies, 95) * 1000),
        "model_parameters": sum(p.numel() for p in model.parameters()),
        "checkpoint_size_bytes": checkpoint_path.stat().st_size,
        "signer_independent_evaluation": False,
        "limitation": "Signer IDs are unavailable; signers may overlap across splits.",
    }
    (experiment_dir / "test_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    (experiment_dir / "per_class_metrics.json").write_text(
        json.dumps(per_class, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (experiment_dir / "confusion_matrix.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["true\\predicted", *class_names])
        for class_name, row in zip(class_names, matrix.tolist()):
            writer.writerow([class_name, *row])
    test_paths = loaders["test"].dataset.records["relative_path"].tolist()
    prediction_rows = [
        [path, idx_to_class[truth], idx_to_class[prediction], confidence]
        for path, truth, prediction, confidence in zip(
            test_paths, true_ids, predicted_ids, confidences
        )
    ]
    headers = ["relative_path", "true_label", "predicted_label", "confidence"]
    for output_name, rows in (
        ("test_predictions.csv", prediction_rows),
        ("misclassified_predictions.csv", [row for row in prediction_rows if row[1] != row[2]]),
    ):
        with (experiment_dir / output_name).open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

    print(json.dumps(metrics, indent=2))
    print(f"Per-class metrics: {experiment_dir / 'per_class_metrics.json'}")
    print(f"Confusion matrix: {experiment_dir / 'confusion_matrix.csv'}")


if __name__ == "__main__":
    main()
