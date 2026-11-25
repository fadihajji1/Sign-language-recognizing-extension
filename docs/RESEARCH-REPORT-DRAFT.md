# Isolated Tunisian Sign Language Recognition from Images

## Progress report and preliminary evaluation

**Draft status:** Prepared 24 November 2026; contributor/teacher review needed  
**Project stage:** Camera-to-model prototype implemented; research report draft in progress

## Abstract

This project develops an academic prototype for recognizing isolated
Tunisian Sign Language (TSL) signs from images. The intended user
experience is a person signing in front of a camera while the system
shows recognized signs to a communication partner. The starting W7CH
dataset contains still images, so the current classifier predicts one of
57 labels per image and cannot interpret movement or full signed
sentences. The dataset was audited, split into training, validation, and
test manifests, and used to train ResNet18 and MobileNetV3 Small image
classifiers. A FastAPI service and React camera interface sample camera
frames and display stable predictions. In the longer CUDA experiments,
ResNet18 achieved 99.55% test accuracy and 99.62% macro F1; MobileNetV3
Small achieved 96.54% accuracy and 96.24% macro F1. These are preliminary
results from an image-level random split without signer separation. They
must not be interpreted as evidence of signer-independent or real-world
continuous-sign recognition.

## 1. Introduction

Sign-language recognition can support communication between TSL users
and people who do not know TSL. This project studies a limited first
step: classifying isolated sign images into the labels provided by the
W7CH dataset. The initial objective is to document the data pipeline,
train reproducible image-classification baselines, evaluate their
behavior, and expose one model through an API.

The target product scenario is camera-based: a person signs while
communicating, and the application presents recognized signs. The
current interface samples a camera frame about every 900 ms. A still
image model predicts each frame independently, and the UI waits for
agreement across recent confident predictions to reduce flicker. The UI
filter does not make the model temporal: it does not recognize hand
motion or combine signs into a sentence.

## 2. Dataset

### 2.1 Source and audit

The project uses the W7CH *First-ever Tunisian Sign Language Dataset*.
The source directory is kept unchanged. The audit found 4,424 readable
image files: 4,423 images in the 57 class folders and one root-level
`interfaces.png` image with no verified class label. The unlabeled image
was excluded. The audit found no unreadable files and 16 exact duplicate
content groups. Most images are 224 × 224 pixels; one image is 767 × 766.

Class labels are inferred from the sign-label folder below each of the
five category folders: Demandes, Destinations, Famille, Jours, and
Transport. The original label spellings, including `métro`, are
preserved. No English translations are inferred.

### 2.2 Train/validation/test split

The verified split was generated with seed 42 and target proportions of
70/15/15. Exact-hash groups were assigned to one split to avoid exact
duplicate leakage across splits.

| Split | Images | Classes |
|---|---:|---:|
| Training | 3,096 | 57 |
| Validation | 663 | 57 |
| Test | 664 | 57 |
| Total | 4,423 | 57 |

The split has zero exact-hash leaks. Hashing does not detect images that
are visually identical but encoded differently. Signer identities are
not available in the usable metadata; the split is not signer
independent and may place images of the same person in different
subsets.

## 3. Preprocessing and training method

Images are opened read-only with Pillow, converted to RGB, resized to
224 × 224, converted to tensors, and normalized using ImageNet channel
means and standard deviations. Mild affine and brightness/contrast
augmentation is applied only to training images. Horizontal flips are
not used because mirroring may change sign meaning. Validation and test
transforms are deterministic.

The stable class-to-index mapping is derived from the 57 labels across
the verified manifests and saved with each experiment. Training uses
cross-entropy loss, AdamW, seed 42, batch size 16, learning rate 0.001,
weight decay 0.0001, and random initialization (`weights=None`). The
best checkpoint is selected by validation accuracy. The test split is
not used for checkpoint selection.

The active environment uses Python 3.15.0, PyTorch 2.15.0+cu134,
Torchvision 0.29.2+cu134, NumPy 2.5.4, Pandas 3.1.0, and Pillow 13.0.0.
CUDA was verified on an NVIDIA GeForce RTX 4060 Laptop GPU. Training
and evaluation use CUDA by default.

## 4. Models

Two image classifiers were implemented:

- **ResNet18:** 11,205,753 parameters.
- **MobileNetV3 Small:** 1,576,281 parameters.

Both models were trained from random initialization. An earlier
two-epoch run showed that the training and evaluation paths worked, but
was too short for a meaningful architecture comparison. Longer
20-epoch CUDA runs were subsequently made; each checkpoint was selected
by validation accuracy. The resulting comparisons remain limited by the
dataset split and the absence of signer-level evaluation.

## 5. Evaluation

### 5.1 Metrics

| Model | Best epoch | Test accuracy | Macro precision | Macro recall | Macro F1 | Mean model latency/image | Parameters | Checkpoint size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ResNet18 | 17 | 99.55% | 99.61% | 99.66% | 99.62% | 0.98 ms | 11,205,753 | 44.90 MB |
| MobileNetV3 Small | 13 | 96.54% | 96.59% | 96.53% | 96.24% | 0.53 ms | 1,576,281 | 6.44 MB |

Latency is model-only on the RTX 4060 during batched inference. It does
not include frame capture, JPEG encoding, image preprocessing, HTTP
overhead, or browser rendering. Timing is hardware and batch dependent.

The per-class metrics, confusion matrices, and individual predictions
are saved under each experiment directory. Misclassified predictions
include source-relative image paths for qualitative inspection.

### 5.2 Interpretation

On this split, ResNet18 scored higher, while MobileNetV3 Small used fewer
parameters and had lower measured model-only latency. The high test
scores should be treated cautiously: images were split at the image
level, signer identity is unavailable, and the dataset is small. Related
recording conditions or signers may be represented across training and
test subsets. These scores do not establish performance for new signers,
different cameras, uncontrolled environments, or complete signing
utterances.

## 6. Camera interface and inference service

FastAPI loads the saved ResNet18 checkpoint at service startup by
default. It provides:

- `GET /health` for readiness;
- `GET /model` for architecture, version, and class information;
- `POST /predict` for an uploaded image and top predictions.

Uploads are validated, limited to 10 MiB, processed in memory, and not
stored by the API. The inference transform matches evaluation
preprocessing. The React interface obtains camera permission, shows a
live preview, and sends a JPEG frame about every 900 ms. It prevents
overlapping requests and requires the same label in at least two of the
latest three confident predictions before displaying that label. This
reduces single-frame flicker but is not temporal sign recognition. A
local image endpoint check returned `car` at 99.99% confidence; this is a
smoke check, not an independent accuracy result.

## 7. Limitations and ethical scope

1. **Isolated signs only.** W7CH supplies static images, not labeled
   video sequences. Motion-based recognition and sentence translation
   are out of scope for the current model.
2. **No signer-independent test.** Signer IDs are unavailable, so the
   reported split cannot measure generalization to unseen signers.
3. **Limited dataset size and variety.** Scores may not transfer to
   different cameras, lighting, backgrounds, distances, or real
   conversations.
4. **No calibrated confidence guarantee.** The confidence value is a
   softmax score. The low-confidence UI threshold is a usability cue,
   not a calibrated probability of correctness.
5. **No validated translations.** The application shows dataset labels;
   it does not translate them into Arabic, French, or English.
6. **Not a professional interpreter.** The prototype is an academic
   demonstration and should not be relied on for consequential
   communication.
7. **Data rights and attribution.** The source repository and license
   should be checked and cited in any publication or redistribution.

## 8. Future work

- Verify performance with signer-independent splits if signer metadata
  or a new consented video dataset becomes available.
- Inspect confusion-matrix errors and visually review representative
  false predictions.
- Calibrate confidence and measure live end-to-end latency under
  realistic camera conditions.
- Collect consented, labeled TSL video sequences with signer and capture
  metadata before developing temporal models.
- Evaluate hand/body landmark or frame-encoder plus temporal-model
  approaches on proper sequence splits.
- Add a linguistically validated mapping from recognized isolated signs
  to written forms only when reliable annotations are available.

## 9. Reproducibility and artifact locations

- Audit: `data/metadata/audit-v1/`
- Split manifests and summary: `data/splits/v2/`
- Data pipeline: `ml-pipeline/src/tsl_data.py`
- Training: `ml-pipeline/src/train.py`
- Evaluation: `ml-pipeline/src/evaluate.py`
- ResNet18 experiment: `experiments/resnet18-gpu-smoke-v1/`
- MobileNetV3 experiment: `experiments/mobilenetv3-gpu-smoke-v1/`
- API: `backend/app/main.py`
- Camera UI: `frontend/`
- Contributor commands: `setup.md`

For exact run commands, use the root `setup.md`. This is a progress
report draft; final academic submission should add citations in the
required style, an approved license statement, error-image examples,
and any supervisor-requested methodology details.
