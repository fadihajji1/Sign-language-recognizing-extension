# Tunisian Sign Language (TSL) Recognition System

## Updated Step-by-Step Implementation and Progress Record

**Project status updated:** 24 November 2026\
**Current stage:** Phase 9 implemented; paused for user review before Phase 10\
**Working directory (Windows):**
`C:\Users\CALLMEFAD\Desktop\tsl-academic-project-docs`

**GPU policy:** training, evaluation, and inference now default to CUDA.
The environment uses PyTorch 2.15.0+cu134 and Torchvision 0.29.2+cu134.
CUDA was verified on the NVIDIA GeForce RTX 4060 Laptop GPU; a CUDA tensor
operation completed on `cuda:0`.

This document records the work completed so far, the verified dataset
facts, verified data pipeline, initial baseline experiment, and remaining
implementation roadmap. It is intended as the working implementation log for a
beginner-friendly, phase-by-phase project.

------------------------------------------------------------------------

## 1. Project goal and scope

Build a research prototype that recognizes one isolated/static Tunisian
Sign Language (TSL) sign from a single image. The planned first model is
a ResNet18 image classifier. Model comparison, an inference API, and a
user interface come later, after the local model works.

**Scope limitation:** the current dataset is an image dataset. This
first version is not a continuous-sign-language translator and should
not be described as recognizing full sentences or all
motion-based/dynamic signs.

### Planned architecture

``` text
React + Vite user interface (later)
        |
        | sends a still image over HTTP
        v
Python + FastAPI inference API (later)
        |
        | shared inference preprocessing
        v
PyTorch image classifier (ResNet18 baseline)
        ^
        | training and evaluation
        |
Dataset -> audit -> split -> preprocessing -> training -> evaluation
```

No database is required for the first prototype. Node.js with pnpm will be
needed for the React development tooling, not for the Python model
service.

### Project safety and reproducibility rules

1.  **Never edit, rename, move, or overwrite files under
    `data/original/w7ch/`.**
2.  Keep generated artifacts in versioned output directories such as
    `data/metadata/audit-v1/` and `data/splits/v2/`.
3.  Do not train until the dataset audit and split have been reviewed.
4.  Do not train on validation or test images; do not apply training
    augmentation to those sets.
5.  Keep the original class labels. Do not invent English translations
    for the labels.
6.  Save class mappings, random seeds, configuration, checkpoints, and
    metrics for experiments.
7.  Report limitations honestly, particularly the lack of signer IDs and
    the possibility of signer overlap.
8.  Treat the test set as a final evaluation set, not as a way to
    repeatedly tune model choices.

------------------------------------------------------------------------

## 2. Current status at a glance

  -----------------------------------------------------------------------
  Phase                   Focus                   Status
  ----------------------- ----------------------- -----------------------
  Phase 0                 Environment/project     Completed sufficiently
                          setup                   to run project scripts
                                                  from an activated
                                                  `.venv`

  Phase 1                 Dataset audit and       Completed
                          inspection              

  Phase 2                 Label interpretation    Completed; `v2`
                          and                     manifests verified
                          train/validation/test   
                          split                   

  Phase 3                 Image preprocessing and Completed; dependencies
                          PyTorch data loaders    verified and loader check
                                                  passed

  Phase 4                 ResNet18 baseline       Completed: CPU baseline
                          training                and CUDA smoke run

  Phase 5                 Evaluation and error    Completed: held-out CPU
                          analysis                and CUDA smoke evaluations

  Phase 6                 Model comparison        Completed initial
                                                  two-epoch CPU smoke comparison

  Phase 7                 FastAPI inference       Completed: service,
                          service                 model loading and
                                                  endpoints implemented

  Phase 8                 React interface         Implemented: camera preview,
                                                  camera controls and predicted-
                                                  sign UI; API integration deferred

  Phase 9                 Camera-to-model         Implemented: sampled frames,
                          integration              local API predictions, and
                                                   UI error/result states

  Phase 10                Research report and     Planned
                          future work             
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 3. Phase 0 --- Environment and project setup

### Completed/verified

-   The project is being worked on in PowerShell on Windows.

-   The project root is:

    `C:\Users\CALLMEFAD\Desktop\tsl-academic-project-docs`

-   The active terminal prompt shows `(.venv)`, indicating the virtual
    environment is activated.

-   The split-generation script can be run from the project root.

### Environment verification

The current command to verify which Python is active is:

``` powershell
python -c "import sys; print(sys.executable)"
```

Expected path should end with:

``` text
tsl-academic-project-docs\.venv\Scripts\python.exe
```

------------------------------------------------------------------------

## 4. Phase 1 --- Dataset audit and inspection

**Status: COMPLETED**

### Dataset layout confirmed

The source images are under:

``` text
data/
└── original/
    └── w7ch/
        ├── Data/
        │   ├── Demandes/
        │   │   └── <sign-label>/
        │   │       └── image files
        │   ├── Destinations/
        │   ├── Famille/
        │   ├── Jours/
        │   └── Transport/
        └── interfaces.png
```

There are five semantic categories. The correct sign label is the folder
immediately below the category, for example:

``` text
Data/Demandes/3aslema/3aslema(1).jpg
```

-   Category: `Demandes`
-   Sign class: `3aslema`

The category folders are not themselves the image-class labels.

### Audit findings

The inspection carried out in this project established:

-   **4,424** image files were found in total.
-   **4,424** files were readable.
-   **57** named sign classes were identified beneath the five category
    folders.
-   **4,423** images belong to those 57 sign classes and are eligible
    for the current classification task.
-   One root-level image, `interfaces.png`, has no verified class label
    and is excluded from the split.
-   Most class images are 224 × 224 pixels; one image was observed at
    767 × 766 pixels.
-   **16 exact duplicate-content groups** were detected during the
    audit.
-   Original images have not been modified.

Audit artifacts are located at:

``` text
data/metadata/audit-v1/
├── dataset-audit.md
├── dataset-audit.json
├── class_counts.csv
├── images.csv
├── exact_duplicates.json
└── unreadable_images.csv
```

The original dataset README/license should be retained and the dataset
attribution/license should be checked before publication or
redistribution.

### Why `interfaces.png` is excluded

It is a root-level image and does not have a verified sign-class label
in the folder structure. It should remain untouched and excluded unless
its label can be confirmed from reliable dataset documentation.

------------------------------------------------------------------------

## 5. Phase 2 --- Label interpretation and dataset splitting

**Status: COMPLETED, with limitations documented**

### Correct class structure

The 57 sign classes are arranged in these five categories:

-   **Demandes (24):** `3aslema`, `5adamet`, `assam`, `barnamjk`,
    `chabeb`, `cv`, `demande`, `enti`, `labes`, `lyoum`, `mar7ba`,
    `n3awnek`, `nekteblk`, `non`, `oui`, `radio`, `se7a`, `siye7a`,
    `t7eb`, `ta3lim`, `ta3raf`, `ta9ra`, `telvza`, `tha9afa`
-   **Destinations (8):** `baladya`, `banka`, `bousta`, `dar`, `ma7kma`,
    `mostawsaf`, `sbitar`, `wzara`
-   **Famille (12):** `3ayla`, `5al-3am`, `5ou`, `bent`, `bou`, `eben`,
    `jad`, `jadda`, `mar2a`, `o5t`, `om`, `tfol`
-   **Jours (7):** `5mis`, `a7ad`, `erb3a`, `jom3a`, `sebt`, `thleth`,
    `thnin`
-   **Transport (6):** `car`, `karhba`, `louage`, `métro`, `taxi`,
    `train`

### Split strategy and results

The current split was generated with seed `42` and target proportions
70% / 15% / 15%.

Command used:

``` powershell
python ml-pipeline/tools/create_splits.py --data-dir data/original/w7ch --output-dir data/splits/v2 --seed 42 --train 0.70 --val 0.15 --test 0.15
```

Verified result:

  Split             Images   Approximate proportion   Classes
  ------------ ----------- ------------------------ ---------
  Training           3,096                      70%        57
  Validation           663                      15%        57
  Test                 664                      15%        57
  **Total**      **4,423**                 **100%**    **57**

The generated files are:

``` text
data/splits/v2/
├── train.csv
├── val.csv
├── test.csv
└── split-summary.md
```

### Manifest verification completed

Each CSV was checked in PowerShell:

-   `train.csv`: 3,096 rows, 57 distinct labels, 0 missing image paths.
-   `val.csv`: 663 rows, 57 distinct labels, 0 missing image paths.
-   `test.csv`: 664 rows, 57 distinct labels, 0 missing image paths.

The CSVs contain the correct accented class label `métro`. The summary
report displays `mÃ©tro` in its per-class table; this appears to be a
text-encoding issue in the Markdown report. The verified CSV label is
correct. Do not rename the original folder or manually edit the CSVs to
fix the report display.

The split report records **zero exact duplicate-hash leaks across
splits**. Identical file contents are kept together in one split, but
visually identical images saved with different encodings may not be
detected by exact hashing.

### Important script correction

The split generator originally treated the first path component as the
class label, which incorrectly interpreted the wrapper folder `Data` as
the only class. The script was corrected to validate the path structure
and infer:

-   `parts[1]` as category
-   `parts[2]` as sign label

A `py_compile` syntax check passed after the indentation correction. The
new `v2` split generated 57 classes correctly.

### Do not use the old split

`data/splits/v1/` contains an earlier invalid split generated when the
script treated `Data` as the label. **Do not train from `v1`.** Use the
verified `data/splits/v2/` manifests.

### Limitations

-   Signer IDs are unavailable, so the current split cannot guarantee
    signer-independent evaluation. Images of the same signer may appear
    across splits.
-   The dataset has relatively small classes. The split report should be
    reviewed for per-class sample counts before interpreting metrics.
-   Exact hash checks do not catch all visual duplicates or
    near-duplicates.
-   `interfaces.png` remains excluded because its label is unverified.

------------------------------------------------------------------------

## 6. Phase 3 --- Image preprocessing and PyTorch data loaders

**Status: COMPLETED**

### Goal

Create a reusable PyTorch data pipeline that reads the verified CSV
manifests, loads images without modifying source files, applies
consistent preprocessing, and returns image tensors with numeric class
IDs.

### Dependency and loader verification

The earlier missing-PyTorch issue is resolved. Environment and loader
checks now pass:

``` powershell
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); import torchvision; print('Torchvision:', torchvision.__version__); import PIL, pandas; print('Pillow and pandas: OK')"
```

The initial loader check passed on 13 November 2026 using CPU-only wheels;
PyTorch was subsequently replaced with the CUDA build. Current environment:

``` text
PyTorch 2.15.0+cu134, Torchvision 0.29.2+cu134, Pandas 3.1.0,
Pillow 13.0.0, NumPy 2.5.4; CUDA available on the RTX 4060 Laptop GPU.
```

The verified interpreter is the project `.venv` at
`C:\Users\CALLMEFAD\Desktop\tsl-academic-project-docs\.venv\Scripts\python.exe`.

### Verified environment and loader

The verified interpreter is the project `.venv`. Imports passed for
PyTorch 2.15.0+cu134, Torchvision 0.29.2+cu134, Pandas 3.1.0, Pillow
13.0.0, and NumPy 2.5.4. CUDA availability and an actual CUDA tensor
operation were confirmed.

### Loader verification

`python ml-pipeline/src/tsl_data.py` loaded the v2 manifests
(3,096/663/664 images), all 57 classes, and an 8-image batch shaped
`(8, 3, 224, 224)`. Labels were valid `int64` IDs and all tensor values
were finite. Validation/test transforms are deterministic; augmentation
is training-only. Runtime dependencies are listed in
`ml-pipeline/requirements.txt`.

### Re-running the import check

Run this command from the project root:

``` powershell
python -c "import torch, torchvision, pandas, PIL; print('PyTorch:', torch.__version__); print('Torchvision:', torchvision.__version__); print('CUDA available:', torch.cuda.is_available()); print('All required libraries imported successfully.')"
```

### Pipeline implementation

The pipeline implementation is in `ml-pipeline/src/tsl_data.py`; see the
verification result above. Transformations happen in memory and do not
write to the original dataset.

### Augmentation precautions

Start with conservative training-only augmentation, such as mild
rotation, translation, brightness, and contrast changes. Do not use
horizontal flips unless it is established that mirroring preserves the
meaning of every affected sign. Do not augment validation or test data.

### Phase 3 acceptance checklist

Acceptance checks completed:

-   [x] PyTorch, Torchvision, Pillow, and Pandas import successfully.
-   [x] A dataset item returns a tensor of shape `3 × 224 × 224` and a
    valid integer label.
-   [x] All three loaders read the correct CSV and image paths.
-   [x] A training batch loads with the expected dimensions.
-   [x] All 57 class names map to stable integer IDs.
-   [x] Transforms run in memory; source images are not written.
-   [x] Validation/test transforms do not include random training
    augmentation.
-   [x] Preprocessing settings and mapping are saved with each experiment.

------------------------------------------------------------------------

## 7. Phase 4 --- First model: ResNet18 baseline

**Status: COMPLETED for the initial two-epoch smoke baseline.**

`ml-pipeline/src/train.py` trains ResNet18 with random initialization,
AdamW and cross-entropy. It uses the v2 manifests, selects checkpoints
by validation accuracy, and stores configuration, class mapping, epoch
logs, and best checkpoint in `experiments/resnet18-baseline-v1/`.
Pretrained weights are disabled so the run does not require a weights
download. Command used:

``` powershell
python ml-pipeline/src/train.py --epochs 2 --batch-size 16 --device cpu
```

Training accuracy rose from 0.2506 to 0.5048; validation accuracy rose
from 0.3575 to 0.7300. This short run confirms the training path; it is
not a tuned or converged model. The checkpoint is 44,902,859 bytes
(about 42.8 MiB). Artifacts are in `experiments/resnet18-baseline-v1/`.
Use a new output directory for longer runs to preserve this baseline.

After CUDA was enabled, a separate GPU smoke run was performed with:

``` powershell
python ml-pipeline/src/train.py --architecture resnet18 --epochs 2 --batch-size 16 --device cuda --output-dir experiments/resnet18-gpu-smoke-v1
```

This run used the RTX 4060. Training accuracy reached 0.4758 and
validation accuracy 0.5973. The checkpoint and configuration are saved
separately under `experiments/resnet18-gpu-smoke-v1/`; the API now uses
this GPU-run checkpoint by default.

Training procedure:

1.  Set reproducible random seeds.
2.  Load a ResNet18 architecture.
3.  Replace the final classification layer with 57 outputs.
4.  Decide whether pretrained weights are available and appropriate for
    the experiment; record the choice.
5.  Train for a short smoke test (e.g. 2--3 epochs) before longer runs.
6.  Track training and validation loss/accuracy.
7.  Save the best checkpoint based on validation performance.
8.  Save class-to-index mapping, configuration, dependency versions, and
    logs.
9.  Keep the test set out of model selection.

**Deliverables:** checkpoint, training log, configuration, and class
mapping.

------------------------------------------------------------------------

## 8. Phase 5 --- Evaluation and error analysis

**Status: COMPLETED for the initial smoke baseline.**

`ml-pipeline/src/evaluate.py` evaluates only the test manifest. It saves
overall and per-class metrics, a confusion matrix, and individual
predictions under the experiment directory. It also writes
`misclassified_predictions.csv` with source-relative paths to help inspect
error cases. Latency is model-only and
does not include image loading, API, or network overhead.

``` powershell
python ml-pipeline/src/evaluate.py --device cpu
```

After training choices are finalized:

1.  Evaluate on the test set.
2.  Report test accuracy, macro precision, macro recall, macro F1,
    per-class F1, and a confusion matrix.
3.  Inspect representative misclassifications.
4.  Record model size and inference latency.
5.  State clearly that signer-independent evaluation is not possible
    without signer IDs.
6.  Avoid claims that a high dataset score proves robust real-world TSL
    recognition.

**Deliverables:** evaluation metrics, confusion matrix, error examples,
and limitations.

The first test evaluation used all 664 test images once:

| Metric | Result |
|---|---:|
| Accuracy | 0.7590 |
| Macro precision | 0.7352 |
| Macro recall | 0.7308 |
| Macro F1 | 0.6959 |
| Mean model latency per image | 11.85 ms (CPU, batch inference) |
| Parameters | 11,205,753 |

Full per-class metrics, confusion matrix, and predictions are saved in
the experiment directory. Latency excludes image loading and API/network
overhead. The score is from only two epochs of random initialization, so
it is an initial smoke result, not evidence of robust recognition.
Signer IDs are unavailable and may overlap across splits.

The subsequent CUDA evaluation of the GPU smoke checkpoint also used the
664-image test set:

| Metric | CUDA result |
|---|---:|
| Accuracy | 0.5633 |
| Macro F1 | 0.4895 |
| Mean model latency per image | 1.03 ms (batch inference) |

These short-run results are separate experiments and should not be
interpreted as a controlled CPU-versus-GPU accuracy comparison. The
CUDA-run artifacts are saved in `experiments/resnet18-gpu-smoke-v1/`.

------------------------------------------------------------------------

## 9. Phase 6 --- Model comparison

**Status: initial two-epoch comparison completed.**

Compare ResNet18 with at least one lightweight alternative such as
MobileNetV3. Use the same splits, evaluation protocol, and reporting
format. Compare macro F1, accuracy, latency, and model size rather than
assuming a larger model is better.

`ml-pipeline/src/models.py` provides shared constructors for ResNet18 and
MobileNetV3 Small. The trainer accepts `--architecture`, evaluation
reconstructs the saved architecture, and
`ml-pipeline/src/compare_experiments.py` aggregates recorded metrics.
Both models used the v2 splits, seed 42, random initialization, and two
CPU epochs. These are the original CPU smoke runs; use the CUDA commands
in `setup.md` for future training. Results are in
`experiments/model-comparison-v1/comparison.csv`:

| Model | Test accuracy | Macro F1 | Mean latency/image | Parameters | Checkpoint |
|---|---:|---:|---:|---:|---:|
| ResNet18 | 0.7590 | 0.6959 | 11.85 ms | 11,205,753 | 42.8 MiB |
| MobileNetV3 Small | 0.0361 | 0.0061 | 1.59 ms | 1,576,281 | 6.1 MiB |

This is a smoke comparison, not a fair final architecture conclusion:
both models were trained from scratch for only two epochs, and
MobileNetV3 Small is severely underfit. Use a longer, validation-selected
training schedule before drawing comparative conclusions. Test metrics
are final for these checkpoints and should not be used to tune them.

------------------------------------------------------------------------

## 10. Phase 7 --- FastAPI inference service

**Status: implementation complete.**

Create a Python API with:

-   `GET /health`
-   `GET /model`
-   `POST /predict`

Load the trained model once at startup. Validate uploaded images, apply
exactly the same preprocessing used for evaluation, and return the real
class label, confidence, and model version. Handle invalid images and
errors explicitly.

Implemented in `backend/app/main.py`, with startup model loading from
the CUDA ResNet18 smoke experiment by default. `TSL_EXPERIMENT_DIR` selects another
saved experiment. Preprocessing reuses the deterministic transform from
the training pipeline. The service includes readiness reporting,
architecture and label metadata, image validation (10 MiB upload cap),
top-five predictions, and a configurable low-confidence marker. Uploads
stay in memory. Install/run details and endpoint shapes are in
`backend/README.md`. Runtime dependencies are listed in
`ml-pipeline/requirements.txt`.

------------------------------------------------------------------------

## 11. Phase 8 --- React interface (implemented; awaiting review)

The `frontend/` project provides a responsive React + Vite + TypeScript
camera-first interface. It requests camera permission, shows a live
preview, handles permission errors, and reserves an area immediately
below the camera for the predicted sign label and a separate area for
future local-AI words or characters. File upload is excluded by design.
Phase 9 connects sampled camera frames to the local API and returns real
model predictions. The UI is organized into `BrandHeader`,
`CameraRecognition`, `RecognitionPanel`,
`GeneratedOutput`, and `AboutNote` components. Manual pnpm install/run
commands are in `setup.md`.

------------------------------------------------------------------------

## 12. Phase 9 --- Camera-to-model integration (implemented; awaiting review)

`frontend/src/services/inferenceApi.ts` posts JPEG camera frames to the
local FastAPI service. `CameraRecognition` samples one frame every 900 ms,
prevents overlapping requests, cancels an in-flight request when the
camera stops, and renders API failures in the interface. The result panel
shows the returned label, confidence, model version, and low-confidence
state. Camera frames remain in memory and are not stored.

The local endpoint was checked using an existing W7CH `car` image. It
returned the `car` label at 99.99% confidence. The browser UI must still
be run locally and granted camera permission by the user. The words and
characters panel remains a future mapping/sequence layer; the current
model classifies one isolated sign and does not translate a sequence.

------------------------------------------------------------------------

## 13. Phase 10 --- Research report and future work (planned)

Document the dataset and license, audit, class definitions, split
procedure, preprocessing, model architecture, hyperparameters, random
seeds, dependency versions, metrics, failure cases, latency, and
limitations.

Continuous/dynamic TSL recognition, sentence translation, and
browser-extension integration are future work that require additional
suitable data and a stable model/API. They are not completed features of
the current prototype.

------------------------------------------------------------------------

## 14. Troubleshooting notes

### `ModuleNotFoundError: No module named 'torch'`

Verify `sys.executable` and install packages using `python -m pip` in
the active `.venv`.

### Split script reports no eligible images

Check the actual folder layout and the script's path-component logic.
The verified structure for this dataset is
`Data/<category>/<sign-label>/<image>`. The corrected script and `v2`
manifests now work.

### `mÃ©tro` appears in the report

The CSV manifests have the correct `métro` label. The issue is confined
to the Markdown summary's text encoding/display. Do not rename the
folder or manually rewrite the CSVs.

### `data/splits/v1` has one class named `Data`

This is the invalid earlier split. Do not use it for training. Use
`data/splits/v2/`.

### CUDA environment verified

The earlier ResNet18 and MobileNetV3 smoke runs used CPU-only PyTorch.
PyTorch now reports CUDA available and identifies the NVIDIA GeForce RTX
4060 Laptop GPU. Training/evaluation default to CUDA and the API requires
CUDA by default. Explicitly pass `--device cuda` in documented model
commands; no future model run should silently fall back to CPU. See
`setup.md` for contributor workflows.

------------------------------------------------------------------------

## 15. Current pause point

Phase 9 is implemented and documented. Stop here for user review. After
confirmation, Phase 10 will compile the academic report, including the
camera-to-model integration method and its limitations.

