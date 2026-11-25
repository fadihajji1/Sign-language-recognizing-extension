# CHECKPOINT.md

# Academic Project Checkpoint

## 1. Current Definition

**Project:** Tunisian Sign Language AI Recognition System

**Domain:** Computer Vision / Deep Learning / Accessibility

**Initial objective:** Isolated Tunisian Sign Language recognition.

**Interface:** React.js

**AI service:** Python + FastAPI

**Neural network:** PyTorch

**Future deployment target:** Browser extension for online meetings.

## 2. Current Architecture Decision

The project will NOT implement:

- Node.js backend
- authentication
- login
- user accounts
- database
- user management

Node.js remains only as the frontend development/runtime toolchain for npm/Vite.

Architecture:

```text
React
  ↓
FastAPI
  ↓
PyTorch
```

## 3. Dataset Decision

Start with the W7CH dataset.

Source facts:

- 4,423 images
- 57 signs
- 7 people
- 224×224
- five categories
- varying image conditions

Source: W7CH GitHub repository. citeturn1view0

## 4. Dataset Modification Rule

Do not modify the original dataset.

Create:

```text
W7CH original
      ↓
Audit
      ↓
Cleaned/processed copy
      ↓
Augmented training set
```

## 5. Checkpoint 01 — Dataset Audit

Tasks:

- [ ] Download source dataset
- [ ] Preserve original copy
- [ ] Verify all 57 classes
- [ ] Count samples per class
- [ ] Inspect class imbalance
- [ ] Find corrupted images
- [ ] Find exact duplicates
- [ ] Inspect image quality
- [ ] Determine whether signer identity can be recovered
- [ ] Create dataset report

Deliverable:

```text
dataset-audit.md
```

## 6. Checkpoint 02 — Preprocessing

Tasks:

- [ ] Define image format
- [ ] Define input resolution
- [ ] Normalize images
- [ ] Create preprocessing script
- [ ] Generate processed dataset
- [ ] Verify output counts

Deliverable:

```text
preprocessing.py
preprocessing.json
```

## 7. Checkpoint 03 — Augmentation

Start conservatively:

- [ ] small rotation
- [ ] small translation
- [ ] brightness variation
- [ ] contrast variation
- [ ] controlled scaling/cropping

Do not automatically use horizontal flipping.

Evaluate whether a transformation changes the meaning of a sign before using it.

## 8. Checkpoint 04 — Dataset Split

Preferred:

```text
Train
Validation
Test
```

If signer metadata is available:

```text
Train signers
Validation signer(s)
Test signer(s)
```

If not available:

- [ ] document limitation
- [ ] avoid claiming signer-independent evaluation

## 9. Checkpoint 05 — Baseline Model

Recommended first experiment:

**ResNet18 transfer learning**

Tasks:

- [ ] baseline CNN
- [ ] training script
- [ ] validation
- [ ] test
- [ ] confusion matrix
- [ ] classification report
- [ ] model checkpoint

## 10. Checkpoint 06 — Model Comparison

Possible candidates:

```text
ResNet18
MobileNetV3
EfficientNet-B0
ResNet50
Small ViT
```

Compare:

```text
Accuracy
Macro F1
Per-class F1
Parameters
Inference latency
Model size
```

Do not select the most complex model without experimental justification.

## 11. Checkpoint 07 — AI API

Implement:

```text
GET  /health
GET  /model
POST /predict
```

Tasks:

- [ ] FastAPI
- [ ] model loading
- [ ] preprocessing
- [ ] inference
- [ ] response schema
- [ ] error handling
- [ ] API tests

## 12. Checkpoint 08 — React Interface

Implemented in `frontend/`:

- [x] camera permission and live preview
- [x] camera-stop control and permission-error feedback
- [x] prediction and confidence presentation states
- [x] error and privacy messaging
- [x] sample camera frames and send them to FastAPI

## 13. Checkpoint 09 — Real-Time Recognition

Tasks:

- [ ] frame sampling
- [ ] inference timing
- [ ] FPS measurement
- [ ] prediction smoothing
- [ ] confidence threshold
- [ ] CPU/GPU benchmark

## 14. Checkpoint 10 — Academic Evaluation

Prepare:

```text
Dataset methodology
Model methodology
Experimental setup
Results
Confusion matrix
Error analysis
Performance analysis
Limitations
```

The project should explain not only how accurate the model is, but also where and why it fails.

## 15. Checkpoint 11 — Dynamic TSL Research

Only after the static model is complete.

Tasks:

- [ ] identify suitable video datasets
- [ ] investigate public TSL sequence resources
- [ ] define sequence format
- [ ] collect additional videos if necessary
- [ ] define signer metadata
- [ ] temporal model
- [ ] dynamic-sign evaluation

A public TSL dataset-building project describes collecting videos at 30 FPS and 720p for sequence classification, which provides a useful reference for designing a future video-data protocol. citeturn0search3

## 16. Checkpoint 12 — Continuous Translation

Future research:

```text
TSL video
 ↓
Temporal model
 ↓
TSL sequence
 ↓
Translation model
 ↓
Arabic/French/English
```

This is not part of the initial dataset/model claim.

## 17. Checkpoint 13 — Browser Extension

Final-stage only.

Tasks:

- [ ] verify stable inference API
- [ ] define extension permissions
- [ ] determine online-meeting integration mechanism
- [ ] build minimal extension
- [ ] connect extension to existing AI API
- [ ] test latency
- [ ] test privacy behavior
- [ ] evaluate meeting usability

The extension should reuse the already-developed AI service rather than requiring the ML system to be rebuilt.

## 18. Current Research Risks

### Small number of participants

The initial dataset has seven people.

### Class imbalance

The dataset contains different numbers of images per class.

### Static-only data

The dataset does not solve temporal movement recognition.

### Dataset/license metadata

The GitHub repository and Mendeley record currently show different license information and should be treated carefully. citeturn1view0turn0search6

### Generalization

Performance on the original dataset does not necessarily mean reliable performance with new TSL users.

## 19. Current Status

**Status:** Phases 0–9 implemented; Phase 9 awaits user review. The
frontend samples camera frames, sends them to the local FastAPI API, and
shows the returned model label and confidence below the camera. The text
output panel awaits a future mapping and sequence design. After
confirmation, Phase 10 compiles the research report.

Do not begin browser-extension development yet.

Do not introduce Node.js as a backend.

Do not introduce authentication or a database.

Do not claim continuous TSL translation from the initial image dataset.
