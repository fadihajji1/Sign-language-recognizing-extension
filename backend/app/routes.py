"""HTTP endpoints for model information and image prediction."""

import io

import torch
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from PIL import Image, UnidentifiedImageError

from settings import LOW_CONFIDENCE_THRESHOLD, MAX_UPLOAD_BYTES


router = APIRouter()


@router.get("/health")
async def health(request: Request):
    loaded = request.app.state.bundle is not None
    return {
        "status": "ok" if loaded else "degraded",
        "model_loaded": loaded,
        "model_error": request.app.state.model_error,
    }


@router.get("/model")
async def model_info(request: Request):
    bundle = request.app.state.bundle
    if bundle is None:
        error = request.app.state.model_error or "Unknown model-loading error"
        raise HTTPException(status_code=503, detail=f"Model is unavailable: {error}")
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


@router.post("/predict")
async def predict(request: Request, image: UploadFile = File(...)):
    bundle = request.app.state.bundle
    if bundle is None:
        error = request.app.state.model_error or "Unknown model-loading error"
        raise HTTPException(status_code=503, detail=f"Model is unavailable: {error}")
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
