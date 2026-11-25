"""Backend configuration."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "ml-pipeline" / "src"
DEFAULT_EXPERIMENT = PROJECT_ROOT / "experiments" / "resnet18-gpu-smoke-v1"
EXPERIMENT_DIR = Path(os.getenv("TSL_EXPERIMENT_DIR", str(DEFAULT_EXPERIMENT)))
DEVICE = os.getenv("TSL_DEVICE", "cuda")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("TSL_LOW_CONFIDENCE_THRESHOLD", "0.45"))
