"""Summarize saved evaluation metrics for comparable model runs."""

import argparse
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "experiment_dirs", nargs="+", type=Path,
        help="Experiment directories containing config.json and test_metrics.json",
    )
    parser.add_argument(
        "--output", type=Path,
        default=PROJECT_ROOT / "experiments" / "model-comparison-v1" / "comparison.csv",
    )
    args = parser.parse_args()
    rows = []
    for supplied_dir in args.experiment_dirs:
        experiment_dir = supplied_dir if supplied_dir.is_absolute() else PROJECT_ROOT / supplied_dir
        config = json.loads((experiment_dir / "config.json").read_text(encoding="utf-8-sig"))
        metrics = json.loads((experiment_dir / "test_metrics.json").read_text(encoding="utf-8-sig"))
        rows.append({
            "experiment": config["experiment"],
            "architecture": config["architecture"],
            "initialization": config["initialization"],
            "epochs_requested": config["epochs_requested"],
            "seed": config["seed"],
            "test_images": metrics["test_images"],
            "accuracy": metrics["accuracy"],
            "macro_precision": metrics["macro_precision"],
            "macro_recall": metrics["macro_recall"],
            "macro_f1": metrics["macro_f1"],
            "mean_model_latency_ms_per_image": metrics["mean_model_latency_ms_per_image"],
            "model_parameters": metrics["model_parameters"],
            "checkpoint_size_bytes": metrics["checkpoint_size_bytes"],
            "signer_independent_evaluation": metrics["signer_independent_evaluation"],
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} model summaries to {args.output.resolve()}")


if __name__ == "__main__":
    main()
