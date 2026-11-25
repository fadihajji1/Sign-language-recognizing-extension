"""AI model loading and inference setup."""

import sys

import torch

from settings import DEVICE, EXPERIMENT_DIR, SRC_DIR


if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import build_model  # noqa: E402
from tsl_data import get_transforms  # noqa: E402


def load_inference_bundle():
    checkpoint_path = EXPERIMENT_DIR / "best_model.pt"
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")
    if DEVICE == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is the default device but is unavailable; install the CUDA build of PyTorch. "
            "Set TSL_DEVICE=cpu only for an intentional CPU run."
        )
    device = torch.device(DEVICE)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    class_to_idx = checkpoint["class_to_idx"]
    config = checkpoint["config"]
    model = build_model(config["architecture"], len(class_to_idx))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device).eval()
    return {
        "model": model,
        "device": device,
        "transform": get_transforms(training=False),
        "class_names": [
            name for name, _ in sorted(class_to_idx.items(), key=lambda item: item[1])
        ],
        "config": config,
        "checkpoint_path": checkpoint_path,
    }
