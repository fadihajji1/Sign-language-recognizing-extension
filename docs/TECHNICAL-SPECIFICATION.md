# TECHNICAL-SPECIFICATION.md

# Technical Specification

## 1. Simplified Architecture

The project intentionally uses only the components required for an academic AI prototype:

```text
React + Vite
     │
     │ HTTP/JSON or multipart image
     ▼
Python FastAPI
     │
     ▼
Preprocessing
     │
     ▼
PyTorch Model
     │
     ▼
Prediction
```

There is no application database.

There is no Node.js backend.

Node.js with pnpm remains part of the frontend development toolchain.

## 2. Frontend

### Technology

- React.js
- TypeScript recommended
- Vite
- Browser MediaDevices API
- Fetch API or Axios

### Responsibilities

- camera permission
- camera preview
- frame capture
- sending inference requests
- displaying predictions
- displaying confidence
- displaying errors/loading state
- optionally displaying model information

Suggested structure:

```text
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   ├── types/
│   └── App.tsx
├── public/
├── package.json
└── vite.config.ts
```

## 3. Python AI Service

### Technology

- Python
- FastAPI
- Uvicorn
- PyTorch
- OpenCV
- NumPy
- scikit-learn

### Responsibilities

- receive image/frame
- validate input
- preprocess input
- load model
- perform inference
- calculate confidence
- return prediction
- expose health/model endpoints

Current project structure:

```text
backend/
└── app/main.py              # FastAPI inference endpoints
ml-pipeline/
├── src/                     # Data loading, model, training, evaluation
├── tools/                   # Dataset audit and split generation
├── requirements.txt
└── requirements-audit.txt
experiments/                 # Checkpoints, configs, metrics and predictions
data/                        # Original data, audit results and split manifests
```

The API imports shared model constructors and preprocessing from
`ml-pipeline/src/`. Run commands and the full repository map are in
`setup.md` and the root `README.md`.

## 4. API

### Health

```http
GET /health
```

Example:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### Model

```http
GET /model
```

Example:

```json
{
  "name": "TSL-CNN",
  "version": "1.0.0",
  "classes": 57
}
```

### Prediction

```http
POST /predict
Content-Type: multipart/form-data
```

Example response:

```json
{
  "label": "hello",
  "confidence": 0.94,
  "model_version": "tsl-cnn-1.0.0"
}
```

The exact labels must come from the actual dataset classes rather than being invented.

## 5. Initial Machine-Learning Pipeline

```text
W7CH Dataset
     ↓
Dataset Audit
     ↓
Cleaning
     ↓
Resize
     ↓
Normalization
     ↓
Controlled Augmentation
     ↓
Train / Validation / Test
     ↓
CNN
     ↓
Softmax
     ↓
Prediction
```

## 6. Dataset Audit

Before training:

- count images per class
- inspect class imbalance
- inspect image dimensions
- identify corrupted files
- identify duplicates
- inspect backgrounds
- inspect lighting
- inspect hand orientation
- inspect possible signer grouping
- verify labels

The original W7CH dataset contains unequal numbers of images across its classes. citeturn1view0

## 7. Dataset Modification Policy

Never overwrite the original dataset.

Use:

```text
data/
├── original/
│   └── w7ch-tsl-v1/
├── processed/
│   └── tsl-processed-v1/
├── splits/
│   └── tsl-split-v1/
└── metadata/
    └── dataset-v1.json
```

The original dataset remains the immutable reference.

## 8. Preprocessing

Recommended:

1. load image
2. verify file
3. convert color format
4. resize to model input
5. normalize
6. optionally crop the relevant region

The preprocessing pipeline must be identical between validation/test and production inference, except that training-only augmentation is not applied during inference.

## 9. Augmentation

Recommended training-only transformations:

- small rotation
- small translation
- mild scaling
- brightness variation
- contrast variation
- small crop variation

Avoid uncontrolled transformations.

### Horizontal flip

Do not automatically use horizontal flipping.

Hand orientation can contain information in sign languages. Test whether flipping preserves the semantic label before including it.

## 10. Class Imbalance

The dataset has unequal class sizes.

Possible approaches:

1. class-weighted loss
2. balanced sampling
3. moderate augmentation of minority classes

Do not simply duplicate minority images many times.

The selected method must be documented and evaluated experimentally.

## 11. Baseline Model

Recommended first model:

**ResNet18**

Reason:

- established CNN baseline
- relatively lightweight
- easy to train
- easy to compare against other architectures
- suitable for academic experimentation

Alternative experiments:

- MobileNetV3
- EfficientNet-B0
- ResNet50
- small Vision Transformer

The project should compare models rather than assuming that the most complex model is automatically best.

## 12. Transfer Learning

Recommended experiment:

```text
ImageNet-pretrained CNN
        ↓
Replace classification head
        ↓
57 TSL classes
        ↓
Fine-tune
```

Compare:

- training from scratch
- transfer learning

## 13. Evaluation Split

Preferred:

```text
Training
Validation
Test
```

If signer identities can be established:

```text
Training signers
Validation signer(s)
Test signer(s)
```

This is preferable because the goal is to recognize signs performed by people the model has not memorized.

If signer identities cannot be established from the supplied dataset, document this limitation instead of claiming signer-independent evaluation.

## 14. Advanced Research Model

Only after the static-sign baseline is stable:

```text
Video
 ↓
Frame encoder
 ↓
Temporal Transformer / BiLSTM
 ↓
Dynamic sign
```

For continuous signing:

```text
Video sequence
 ↓
Spatial encoder
 ↓
Temporal encoder
 ↓
Sign sequence
 ↓
Language model / translation model
 ↓
Arabic/French/English
```

## 15. Real-Time Inference

Do not run a large model on every browser frame initially.

Use:

```text
Camera
 ↓
Frame sampling
 ↓
Inference
 ↓
Prediction smoothing
 ↓
UI
```

Measure:

- latency per inference
- FPS
- CPU/GPU utilization
- memory usage

## 16. Model Versioning

Every trained model should record:

```text
model_version
dataset_version
architecture
input_size
classes
training_parameters
validation_metrics
test_metrics
training_date
```

## 17. Testing

### AI

- preprocessing tests
- label mapping tests
- model loading tests
- inference tests
- regression tests

### API

- valid image
- invalid image
- missing image
- model unavailable
- malformed request

### React

- camera permission
- loading state
- prediction display
- low confidence
- API unavailable

### Integration

```text
React → FastAPI → Model → FastAPI → React
```

## 18. Browser Extension Compatibility

The FastAPI inference API should remain independent of the React application.

This allows the future extension to use the same API:

```text
React application ─────┐
                       │
                       ▼
                  FastAPI
                       │
                       ▼
                     Model
                       ▲
                       │
Browser extension ─────┘
```

Therefore extension development does not need to start now.
