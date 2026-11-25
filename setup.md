# Contributor setup and phase-by-phase runbook

Updated 24 November 2026. Phases 0–9 are implemented. A Phase 10
research-report draft is prepared for review.

## 0. Environment and first-time setup

Use Windows PowerShell. Install a Python version supported by the pinned
PyTorch CUDA wheels, Node.js/npm, and NVIDIA drivers. Training, evaluation,
and API inference require a CUDA-capable NVIDIA GPU.

### Backend Python environment

From the project root, create the Python environment and install the backend,
model, and dataset dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r ml-pipeline/requirements.txt
```

Check CUDA before starting model work:

```powershell
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'unavailable'); assert torch.cuda.is_available(), 'CUDA is required for model runs'"
```

### Frontend Node.js environment

Open a separate PowerShell window, then install the frontend dependencies:

```powershell
Set-Location frontend
npm install
```

The W7CH source dataset is not included in Git. Obtain it from the
[dataset repository](https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset)
and place its extracted contents under `data/original/w7ch/`, preserving
the existing `Data/<category>/<sign-label>/<image>` layout. Keep original
images unchanged.

Keep the backend and frontend in their separate PowerShell windows when
running the application. The manual start commands are in Phases 7–9 below.

The runtime requirements pin PyTorch 2.15.0 and Torchvision 0.29.2 to
the official CUDA 13.4 wheels. If installation or CUDA detection fails,
follow the current [PyTorch Windows install selector](https://pytorch.org/get-started/locally/)
and verify `torch.cuda.is_available()` before continuing.

Do not edit the source dataset under `data/original/w7ch/`. Generated
audit, split, and experiment outputs belong in their versioned output
folders. The `.gitignore` intentionally excludes original data and
experiment artifacts; retain important outputs outside Git when sharing
an experiment.

## Phase 1 — Dataset audit

The checked-in audit artifacts are under `data/metadata/audit-v1/`.
To recreate them after obtaining the W7CH dataset:

```powershell
python ml-pipeline/tools/audit_dataset.py --data-dir data/original/w7ch --output-dir data/metadata/audit-v1
```

Review `dataset-audit.md`, `class_counts.csv`, and duplicate findings
before proceeding. The audit is read-only with respect to original images.

## Phase 2 — Label manifests and data split

Use the verified `v2` split; do not use the invalid legacy `v1` split.
To regenerate the split:

```powershell
python ml-pipeline/tools/create_splits.py --data-dir data/original/w7ch --output-dir data/splits/v2 --seed 42 --train 0.70 --val 0.15 --test 0.15
```

Review `data/splits/v2/split-summary.md` and confirm 57 classes, 70/15/15
split proportions, and zero exact-hash leaks before training.

## Phase 3 — Preprocessing and data loaders

```powershell
python ml-pipeline/src/tsl_data.py
python ml-pipeline/src/class_mapping.py
```

The loader uses `data/splits/v2`, maps all 57 class names consistently,
resizes images to 224 × 224, applies ImageNet normalization, and applies
augmentation only to training data. The source images are not rewritten.

## Phase 4 — Train a baseline model on GPU

Run a short smoke training first; choose a distinct output directory so
existing experiments remain available:

```powershell
python ml-pipeline/src/train.py --architecture resnet18 --epochs 20 --batch-size 16 --device cuda --output-dir experiments/resnet18-gpu-smoke-v1
```

For a longer experiment, increase `--epochs` and use another output
directory. The script saves the best validation checkpoint, training
log, class mapping, configuration, device, and dependency versions. It
selects checkpoints using validation data only. Never pass `--device cpu`
for a GPU run.

## Phase 5 — Held-out evaluation on GPU

Evaluate each selected checkpoint once, after model choices are fixed:

```powershell
python ml-pipeline/src/evaluate.py --device cuda --experiment-dir experiments/resnet18-gpu-smoke-v1
```

This writes test metrics, per-class metrics, confusion matrix, all test
predictions, and a path-linked misclassification list. Test results are
for final reporting, not repeated model selection. Report that signer
IDs are unavailable and the split may contain signer overlap.

## Phase 6 — Model comparison on GPU

Train the lightweight comparison with the same split, seed, and schedule:

```powershell
python ml-pipeline/src/train.py --architecture mobilenet_v3_small --epochs 20 --batch-size 16 --device cuda --output-dir experiments/mobilenetv3-gpu-smoke-v1
python ml-pipeline/src/evaluate.py --device cuda --experiment-dir experiments/mobilenetv3-gpu-smoke-v1
python ml-pipeline/src/compare_experiments.py experiments/resnet18-gpu-smoke-v1 experiments/mobilenetv3-gpu-smoke-v1
```

The generated comparison CSV includes accuracy, macro metrics, model
latency, parameter count, and checkpoint size. Two-epoch random-init
results are smoke comparisons only; use a longer schedule before making
architecture claims.

## Phase 7 — Run the FastAPI inference service

By default, the API loads `experiments/resnet18-gpu-smoke-v1/best_model.pt`
and requires CUDA. Select a different experiment if desired:

```powershell
$env:TSL_EXPERIMENT_DIR = "experiments/resnet18-gpu-smoke-v1"
$env:TSL_DEVICE = "cuda"
python -m uvicorn main:app --app-dir backend/app --host 127.0.0.1 --port 8000
```

Available endpoints are `GET /health`, `GET /model`, and
`POST /predict` (multipart form field `image`). Uploads are limited to
10 MiB and processed in memory. The API uses the same deterministic
preprocessing as evaluation. Interactive API documentation is at
`http://127.0.0.1:8000/docs` while the service is running.

## Phase 8 — React interface (implemented; awaiting review)

The React + Vite + TypeScript frontend is under `frontend/`. It supports
camera permission, a live preview, camera errors, privacy messaging, and
a predicted-sign area plus a future local-AI words/characters area below
the camera. File upload and drag-and-drop are not part of this interface.

Install and run it from the project root in PowerShell:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally
`http://localhost:5173`). Camera access requires a secure browser context
such as localhost and user permission.

The interface is split into `BrandHeader`, `CameraRecognition`,
`RecognitionPanel`, `GeneratedOutput`, and `AboutNote` components under
`frontend/src/components/`.

## Phase 9 — Camera-to-model integration and stable display

Run FastAPI as described in Phase 7 and the frontend as described in
Phase 8. Keep both running. The browser samples a JPEG frame about every
900 ms, posts it to `POST /predict`, and displays a sign only when the
same label appears in at least 2 of the latest 3 confident predictions.
This reduces brief label flicker. It is a frontend display filter; the
model still classifies each frame independently. The app does not track
hand motion or combine signs into sentences. Frames are kept in memory
and are not saved.

To use the camera, open the local Vite page, select **Open camera**, and
grant browser camera permission. Keep one supported sign clearly in view
for a moment so the predictions can agree. Check the API is running if an
API error appears. Stop the camera with **Stop camera** when finished.

In the local integration check, an existing W7CH `car` image returned
the `car` label at 99.99% confidence. This checks the image API path; it
does not measure live-camera or motion-sign accuracy.

The current interface applies a rolling confidence filter: it shows a
label only after at least two of the latest three confident predictions
agree. This may delay a changed sign by one sample, but it reduces
single-frame flicker. No video sequence model is used.

## Phase 10 — Research report (draft prepared)

Review and revise [`docs/RESEARCH-REPORT-DRAFT.md`](docs/RESEARCH-REPORT-DRAFT.md).
The draft summarizes the dataset audit, split method, preprocessing,
training configurations, model results, camera/API behavior, and
limitations. Before academic submission, add citations in the required
style, confirm dataset licensing and attribution, inspect representative
error images, and incorporate supervisor feedback. Do not claim
continuous sign translation: W7CH provides still images for isolated
image-sign classification.
