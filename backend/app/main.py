"""FastAPI inference service for isolated Tunisian Sign Language images."""

import io
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "ml-pipeline" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import build_model  # noqa: E402
from tsl_data import get_transforms  # noqa: E402


DEFAULT_EXPERIMENT = PROJECT_ROOT / "experiments" / "resnet18-gpu-smoke-v1"
EXPERIMENT_DIR = Path(os.getenv("TSL_EXPERIMENT_DIR", str(DEFAULT_EXPERIMENT)))
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("TSL_LOW_CONFIDENCE_THRESHOLD", "0.45"))


def load_inference_bundle():
    checkpoint_path = EXPERIMENT_DIR / "best_model.pt"
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")
    requested_device = os.getenv("TSL_DEVICE", "cuda")
    if requested_device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is the default device but is unavailable; install the CUDA build of PyTorch. "
            "Set TSL_DEVICE=cpu only for an intentional CPU run."
        )
    device = torch.device(requested_device)
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.bundle = load_inference_bundle()
        app.state.model_error = None
    except Exception as exc:
        app.state.bundle = None
        app.state.model_error = str(exc)
    yield


app = FastAPI(
    title="TSL Recognition API",
    description="Isolated Tunisian Sign Language image recognition.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    loaded = app.state.bundle is not None
    return {
        "status": "ok" if loaded else "degraded",
        "model_loaded": loaded,
        "model_error": app.state.model_error,
    }


@app.get("/model")
async def model_info():
    bundle = app.state.bundle
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model is unavailable")
    config = bundle["config"]
    return {
        "name": "TSL isolated-sign classifier",
        "version": config.get("experiment", "unknown"),
        "architecture": config["architecture"],
        "classes": len(bundle["class_names"]),
        "labels": bundle["class_names"],
        "input_size": config.get("image_size", 224),
        "low_confidence_threshold": LOW_CONFIDENCE_THRESHOLD,
        "scope": "one isolated sign per still image",
    }


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    bundle = app.state.bundle
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model is unavailable")
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload must be an image")
    payload = await image.read(MAX_UPLOAD_BYTES + 1)
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MiB limit")
    try:
        with Image.open(io.BytesIO(payload)) as source:
            source.verify()
        with Image.open(io.BytesIO(payload)) as source:
            image_rgb = source.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    tensor = bundle["transform"](image_rgb).unsqueeze(0).to(bundle["device"])
    with torch.inference_mode():
        probabilities = torch.softmax(bundle["model"](tensor), dim=1)[0]
    top_values, top_indices = torch.topk(
        probabilities, k=min(5, len(bundle["class_names"]))
    )
    confidence = float(top_values[0].item())
    label = bundle["class_names"][int(top_indices[0].item())]
    return {
        "label": label,
        "confidence": confidence,
        "low_confidence": confidence < LOW_CONFIDENCE_THRESHOLD,
        "model_version": bundle["config"].get("experiment", "unknown"),
        "architecture": bundle["config"]["architecture"],
        "top_predictions": [
            {
                "label": bundle["class_names"][int(index.item())],
                "confidence": float(value.item()),
            }
            for value, index in zip(top_values, top_indices)
        ],
        "scope": "isolated sign classification; not continuous translation",
    }
