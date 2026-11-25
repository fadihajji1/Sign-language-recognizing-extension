# Tunisian Sign Language (TSL) Recognition — Beginner Implementation Roadmap

## What we are building

A research prototype that recognizes **one isolated/static TSL sign in one image**. The first dataset is the W7CH First-ever Tunisian Sign Language Dataset described in the project docs. The first model will be a ResNet18 image classifier, followed by measured comparisons. The web app comes only after the model works.

**Important scope limit:** this dataset is described as images, not continuous sign-language videos. The first version will not translate full sentences or reliably recognize motion-based/dynamic signs.

## Architecture

```text
React + Vite (later)
       │ sends image over HTTP
       ▼
Python + FastAPI (later)
       │ preprocessing + inference
       ▼
PyTorch classifier (ResNet18 baseline)
       ▲
       │ trained using
W7CH dataset → audit → split → train → evaluate
```

No database and no Node.js backend are needed. Node.js runs the React development tools; pnpm manages their dependencies.

## Beginner rules

1. Never edit or overwrite `data/original/w7ch/`.
2. Do not train until the dataset audit has been reviewed.
3. Keep test images out of training and augmentation.
4. Keep the actual class/folder names; do not invent English translations.
5. Save the settings and metrics for every experiment.
6. Report limitations honestly, especially the small number of signers and possible signer overlap.
7. A high score on this dataset does not guarantee real-world performance.

## Phases and completion checks

### Phase 0 — Prepare your computer

**Do this**
1. Install Python 3.11 or 3.12, Git, and VS Code.
2. Install the VS Code Python extension.
3. Download and extract this project starter ZIP.
4. In VS Code choose **File → Open Folder** and open `tsl-academic-project-docs`.
5. Open **Terminal → New Terminal** (PowerShell on Windows).

**Verify**
```powershell
python --version
git --version
```
Both commands should print a version. If `python` is not found on Windows, install Python from python.org and select **Add Python to PATH** during installation.

### Phase 1 — Create the Python environment and audit the dataset (START HERE)

**Goal:** verify what is actually in the downloaded dataset before changing anything.

1. Download the W7CH dataset from https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset. Read the repository README and license information first.
2. Extract it. Put the dataset's *existing class folders* inside `data/original/w7ch/`. Do not rename class folders or delete files. If extraction creates an extra wrapper folder, that is okay; the audit script searches recursively.
3. In the VS Code terminal, make sure you are in the project root (the folder containing `backend`, `ml-pipeline`, and `data`).
4. Create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If PowerShell blocks activation, run this only in the current terminal, then activate again:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
5. Install the audit dependencies:
```powershell
python -m pip install --upgrade pip
python -m pip install pillow pandas
```
6. Run the audit:
```powershell
python ml-pipeline/tools/audit_dataset.py --data-dir data/original/w7ch --output-dir data/metadata/audit-v1
```
7. Open `data/metadata/audit-v1/dataset-audit.md`, `class_counts.csv`, and `images.csv`.

**Phase 1 deliverables**
- total readable images and image dimensions
- images per class (if class folders can be inferred)
- corrupted/unreadable file list
- exact duplicate-file-content groups (SHA-256)
- a report of what the script could and could not infer

**Stop and review before continuing** if the image count/classes look wrong, class labels are nested unexpectedly, many files are unreadable, or the dataset's actual layout is unclear. Send me the audit report and a screenshot or pasted folder tree; we will adapt the pipeline to the real layout.

### Phase 2 — Dataset interpretation and split

1. Inspect class names and image samples manually.
2. Confirm whether the dataset has one folder per sign, or a different labeling format.
3. Investigate whether signer identity can be recovered from folder names or metadata.
4. Decide on a reproducible train/validation/test split. If signer IDs are available, prefer signer-independent splitting.
5. Record the random seed and split manifest.
6. Do not augment the validation or test data.

Deliverable: documented split manifest and `dataset-v1.json`.

### Phase 3 — Preprocessing and data loaders

1. Define RGB conversion, image size (start with 224×224), and normalization.
2. Apply augmentation only to training samples: mild rotation, translation, brightness and contrast.
3. Do not use horizontal flips unless you verify they preserve the meaning of each sign.
4. Build PyTorch datasets/data loaders.
5. Test a small batch and display sample images with labels.

Deliverable: tested preprocessing code and a saved configuration.

### Phase 4 — First model: ResNet18 baseline

1. Install PyTorch/torchvision using the official selector: https://pytorch.org/get-started/locally/
2. Replace the pretrained ResNet18 classification head with the number of actual classes found in the audit.
3. Train with a fixed random seed.
4. Save the best validation checkpoint, class-to-index mapping, and training settings.
5. Track train/validation loss and accuracy.
6. Start with a small run (e.g. 2–3 epochs) to prove the pipeline works; only then increase training time.

Deliverable: reproducible baseline checkpoint and training log.

### Phase 5 — Evaluation and error analysis

1. Evaluate the test split once the model/training choices are finalized.
2. Report accuracy, macro precision/recall/F1, per-class F1, and confusion matrix.
3. Inspect misclassified examples.
4. Record inference latency and model size.
5. State whether test subjects overlap with training subjects.

Deliverable: metrics files, confusion matrix, and written limitations.

### Phase 6 — Compare models

Compare ResNet18 against at least one lightweight alternative such as MobileNetV3. Use the same split and evaluation process. Compare accuracy, macro F1, latency, and model size; do not assume the larger model is better.

### Phase 7 — FastAPI inference service

Create `/health`, `/model`, and `POST /predict`. Load the trained model once at startup. Validate uploaded images, use the exact same inference preprocessing as evaluation, and return the real dataset label plus confidence and model version.

### Phase 8 — React user interface

Create a React + Vite + TypeScript interface. First support image upload; then add camera permission, preview, capture, loading/error states, prediction and confidence display.

### Phase 9 — Integration and real-time tests

Connect React to FastAPI. Test valid/invalid inputs, low confidence, API failure, latency and privacy. Only after single-image inference is stable, sample camera frames and smooth predictions.

### Phase 10 — Research report and future work

Document dataset, split, preprocessing, models, hyperparameters, metrics, failure cases, latency, limitations, and reproducibility. Dynamic/continuous TSL and browser-extension integration are future phases requiring suitable sequence data and a stable API.

## Phase gates

Do not skip ahead:
- Phase 1 passes when the audit is generated and the dataset layout is understood.
- Phase 2 passes when class labels and split strategy are confirmed.
- Phase 3 passes when batches load correctly.
- Phase 4 passes when a baseline trains and saves a checkpoint.
- Phase 5 passes when test metrics and limitations are documented.
- API/UI phases start only after the model can predict an image locally.

## Troubleshooting

- `python` not found: reinstall Python and enable PATH, then reopen VS Code.
- Script says no images found: check that extracted image files are under `data/original/w7ch/`; pass the actual folder with `--data-dir`.
- Many classes named like `train`, `test`, or `images`: the script may be treating a wrapper directory as a class. Do not proceed; show me the folder tree so we can set the correct class-root.
- Virtual environment activation blocked: use the temporary PowerShell policy command shown above.
- CPU-only training is okay. GPU acceleration is optional.
