# TSL AI service

FastAPI inference service for the current isolated-sign classifier.

## Install and run

From the project root, with the project virtual environment active:

```powershell
python -m pip install -r ml-pipeline/requirements.txt
python -m uvicorn main:app --app-dir backend/app --host 127.0.0.1 --port 8000
```

The default checkpoint is `experiments/resnet18-gpu-smoke-v1/best_model.pt`.
Set `TSL_EXPERIMENT_DIR` to another experiment directory before starting
the service to serve a different saved checkpoint. The model loads once
at startup. If it cannot load, `/health` returns a degraded status and
prediction requests return HTTP 503.

## Endpoints

- `GET /health` — service and model readiness.
- `GET /model` — architecture, class labels, version, input size, and the
  low-confidence threshold.
- `POST /predict` — multipart form upload with an `image` field. Returns
  the top label, confidence, low-confidence flag, model version, and top
  five candidates.

Uploads are limited to 10 MiB, validated as images, converted to RGB,
then preprocessed with the same deterministic resize and normalization
used for evaluation. The service processes the upload in memory and does
not save it. Confidence below `TSL_LOW_CONFIDENCE_THRESHOLD` (default
`0.45`) is marked as low confidence; this threshold is a UI cue, not a
calibrated probability guarantee.

The service recognizes one supported isolated sign per still image. It
does not translate continuous signing or sentences.
