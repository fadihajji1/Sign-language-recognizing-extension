# ARCHITECTURE.md

# System Architecture

## 1. Architectural Objective

Keep the project as simple as possible while separating the academic AI component from the user interface.

## 2. Final Initial Architecture

```text
┌──────────────────────────────┐
│       React Web App          │
│                              │
│ Camera                       │
│ Prediction UI                │
│ Confidence                   │
└──────────────┬───────────────┘
               │
               │ HTTP
               ▼
┌──────────────────────────────┐
│      Python FastAPI          │
│                              │
│ Request validation           │
│ Image preprocessing          │
│ Model inference              │
│ Prediction formatting        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       PyTorch Model          │
│                              │
│ CNN classifier               │
│ 57 TSL classes               │
└──────────────────────────────┘
```

## 3. Why Node.js Backend Was Removed

The original idea included React + Node.js.

After defining the actual requirements, a separate Node.js backend is unnecessary because there is:

- no authentication
- no user management
- no database
- no application business logic
- no persistent user data
- no administrative API

The Python service already needs to expose an inference API.

Therefore:

```text
React → FastAPI → PyTorch
```

is the cleaner architecture.

### Important distinction

Node.js is still used for:

- pnpm
- Vite
- React development tooling
- frontend dependency management

But it is **not a backend service**.

## 4. Frontend Architecture

```text
frontend/
├── components/
│   ├── CameraView
│   ├── PredictionResult
│   └── ConfidenceIndicator
├── pages/
│   └── RecognitionPage
├── services/
│   └── inferenceApi
├── hooks/
│   └── useCamera
└── types/
```

## 5. AI Architecture

```text
FastAPI
   │
   ├── /health
   ├── /model
   └── /predict
           │
           ▼
     Image Validator
           │
           ▼
     Preprocessor
           │
           ▼
       PyTorch Model
           │
           ▼
     Postprocessor
           │
           ▼
 label + confidence
```

## 6. Runtime Flow

```text
1. User opens application
2. React requests camera permission
3. Camera preview starts
4. User captures a frame
5. React sends frame to FastAPI
6. FastAPI validates input
7. Image is preprocessed
8. Model performs inference
9. Prediction is returned
10. React displays result
```

## 7. Research/Training Flow

Training is separate from runtime inference:

```text
W7CH dataset
      ↓
Dataset audit
      ↓
Preprocessing
      ↓
Augmentation
      ↓
Dataset split
      ↓
Training
      ↓
Validation
      ↓
Test
      ↓
Model artifact
      ↓
FastAPI inference
```

## 8. Browser Extension Architecture — Future

The extension is a final-stage deployment layer.

```text
                 ┌───────────────┐
                 │ React Web App │
                 └───────┬───────┘
                         │
                         ▼
                   ┌───────────┐
                   │ FastAPI   │
                   └─────┬─────┘
                         │
                         ▼
                    ┌────────┐
                    │ Model  │
                    └────────┘
                         ▲
                         │
                 ┌───────┴────────┐
                 │ Browser        │
                 │ Extension      │
                 └────────────────┘
```

The same AI service can therefore serve both the prototype web interface and the eventual extension.

## 9. Deployment

Initial development:

```text
Browser
  ↓
React dev server
  ↓
FastAPI
  ↓
Local model
```

Optional Docker:

```text
┌──────────────┐
│ React        │
├──────────────┤
│ FastAPI      │
├──────────────┤
│ Model        │
└──────────────┘
```

No PostgreSQL container is required.

## 10. Architectural Principles

- Minimal architecture
- AI-first design
- Separation of UI and ML
- No unnecessary backend
- No unnecessary persistence
- Reproducible experiments
- Model versioning
- Extension-ready API
- Privacy by default
