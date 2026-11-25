# Development, Contribution and Setup Guide

> **Legacy planning guide:** the live project folders have since been
> reorganized. Use the root [`README.md`](../README.md) for the current
> structure and [`setup.md`](../setup.md) for run commands.

## 1. Purpose

This document explains how to set up, develop, test, and contribute to the Tunisian Sign Language Recognition project.

It is intended for developers who are already comfortable with:

- VS Code
- Git
- JavaScript/TypeScript
- React
- General software development

but are new to:

- Deep Learning
- PyTorch
- Computer Vision
- Neural Network training
- Dataset preparation

The objective is to make the project reproducible from a completely fresh environment.

---

# 2. Project Overview

The project is a Deep Learning-based Tunisian Sign Language (TSL) recognition system.

The initial system focuses on **isolated sign recognition from images**.

The long-term objective is to make the system usable inside online meetings through a browser extension.

The browser extension is **not the first implementation target**.

The recommended development order is:

```text
Dataset
   ↓
Dataset preparation
   ↓
Neural network training
   ↓
Model evaluation
   ↓
Python inference API
   ↓
React interface
   ↓
Camera inference
   ↓
Real-time recognition
   ↓
Browser extension
```

The research component comes before the final browser-extension integration.

---

# 3. High-Level Architecture

The initial application consists of three main components:

```text
┌─────────────────────────────┐
│       React + Vite          │
│                             │
│  - Simple user interface    │
│  - Camera                   │
│  - Image capture            │
│  - Prediction display       │
└──────────────┬──────────────┘
               │
               │ HTTP
               ▼
┌─────────────────────────────┐
│       Python + FastAPI      │
│                             │
│  - Receive image            │
│  - Preprocess image         │
│  - Run model inference      │
│  - Return prediction        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       PyTorch Model         │
│                             │
│  CNN / Computer Vision      │
│  TSL classifier             │
│                             │
│  Initial 57 classes         │
└─────────────────────────────┘
```

## 3.1 What is not required

The initial project does **not** require:

- Node.js backend
- Express.js
- SQL database
- MongoDB
- Authentication
- Login
- User registration
- User management
- Admin dashboard
- User accounts

Node.js is only required for the React/Vite frontend development environment.

The AI backend is written in Python.

---

# 4. Development Strategy

The project should be developed in the following order.

### Phase 1 — Environment

Install and verify:

- Git
- Python
- Node.js
- pnpm
- VS Code

### Phase 2 — Project Structure

Create separate directories for:

- Frontend
- AI service
- Dataset
- Models
- Experiments
- Documentation

### Phase 3 — Dataset

Start with the W7CH Tunisian Sign Language dataset.

The original dataset must be preserved and must not be modified directly.

### Phase 4 — Dataset Audit

Before training a neural network, inspect:

- Number of images
- Number of classes
- Images per class
- Image dimensions
- Image formats
- Missing files
- Corrupted files
- Duplicate images
- Class imbalance
- Signer/person information
- Lighting variations
- Background variations
- Hand orientation
- Label consistency

### Phase 5 — Preprocessing

Create a reproducible preprocessing pipeline.

### Phase 6 — Baseline Model

Train a first ResNet18 transfer-learning model.

### Phase 7 — Evaluation

Evaluate the model using multiple metrics, not accuracy alone.

### Phase 8 — FastAPI

Expose the trained model through a Python API.

### Phase 9 — React

Build the simple frontend interface.

### Phase 10 — Camera

Connect camera input to the inference pipeline.

### Phase 11 — Real-Time Recognition

Measure and optimize inference performance.

### Phase 12 — Advanced Research

Investigate temporal/continuous sign recognition.

### Phase 13 — Browser Extension

Integrate the validated system into the final browser-extension target.

---

# 5. Project Structure

The recommended project structure is:

```text
tunisian-sign-language-ai/
│
├── frontend/
│
├── ai-service/
│   ├── app/
│   ├── training/
│   ├── evaluation/
│   ├── tools/
│   ├── models/
│   └── requirements.txt
│
├── data/
│   ├── original/
│   │   └── w7ch/
│   ├── processed/
│   ├── splits/
│   └── metadata/
│
├── models/
│
├── experiments/
│
├── docs/
│
├── .gitignore
├── README.md
├── PRODUCT.md
├── TECHNICAL-SPECIFICATION.md
├── ARCHITECTURE.md
├── DATA-MODEL.md
├── CHECKPOINT.md
├── CONTRIBUTION.md
└── CHANGELOG.md
```

---

# 6. Prerequisites

Before starting, install:

- Git
- Python 3.11 or 3.12
- Node.js
- pnpm
- VS Code
- A modern web browser

A GPU is **optional**.

The project can initially be developed and tested on CPU.

---

# 7. Verify the Environment

Open PowerShell in VS Code.

Check Git:

```powershell
git --version
```

Check Python:

```powershell
python --version
```

Check Node.js:

```powershell
node --version
```

Check pnpm:

```powershell
pnpm --version
```

All commands should return a version number.

---

# 8. Create the Project

Create the project directory:

```powershell
mkdir tunisian-sign-language-ai
cd tunisian-sign-language-ai
```

Initialize Git:

```powershell
git init
```

Create the main directories:

```powershell
mkdir frontend
mkdir ai-service
mkdir data
mkdir models
mkdir docs
mkdir experiments
```

Create the dataset directories:

```powershell
mkdir data\original
mkdir data\processed
mkdir data\splits
mkdir data\metadata
```

Create the AI service directories:

```powershell
mkdir backend\app
mkdir ai-service\training
mkdir ai-service\evaluation
mkdir ml-pipeline\tools
mkdir ai-service\models
```

---

# 9. Python Virtual Environment

Python dependencies should be isolated in a virtual environment.

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

The terminal should display something similar to:

```text
(.venv) PS C:\...\tunisian-sign-language-ai>
```

This means the virtual environment is active.

## 9.1 PowerShell activation problem

If PowerShell prevents activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 10. Upgrade pip

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
```

Using `python -m pip` is preferred because it ensures that pip belongs to the currently active Python environment.

---

# 11. Install PyTorch

PyTorch is the main Deep Learning framework used by this project.

Use the official PyTorch installation selector:

[https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

The correct installation depends on:

- Operating system
- Python version
- CPU/GPU
- CUDA support

Do not copy an outdated CUDA installation command from another tutorial.

A CPU installation is sufficient to begin development.

---

# 12. Verify PyTorch

Run:

```powershell
python
```

Then:

```python
import torch

print(torch.__version__)
print(torch.cuda.is_available())
```

Exit Python:

```python
exit()
```

If:

```python
torch.cuda.is_available()
```

returns:

```text
False
```

this is not necessarily an error.

It means PyTorch cannot currently use a CUDA-compatible NVIDIA GPU.

The project can still run on CPU.

---

# 13. Install Python Dependencies

Install the remaining packages:

```powershell
pip install fastapi uvicorn opencv-python numpy pandas scikit-learn matplotlib pillow tqdm torchvision
```

The main packages are:


| Package      | Purpose                               |
| ------------ | ------------------------------------- |
| PyTorch      | Deep Learning                         |
| torchvision  | Computer Vision and pretrained models |
| FastAPI      | AI API                                |
| Uvicorn      | FastAPI server                        |
| OpenCV       | Image/video processing                |
| NumPy        | Numerical operations                  |
| Pandas       | Dataset analysis                      |
| scikit-learn | Evaluation and metrics                |
| Matplotlib   | Graphs and confusion matrices         |
| Pillow       | Image processing                      |
| tqdm         | Progress bars                         |


Save the environment:

```powershell
pip freeze > ml-pipeline\requirements.txt
```

---

# 14. Optional Python Dependencies

Install additional packages only when required.

For hand/camera processing:

```powershell
pip install mediapipe
```

For training visualization:

```powershell
pip install tensorboard
```

For experiment tracking:

```powershell
pip install mlflow
```

These are optional and should not be installed unless the project needs them.

---

# 15. Node.js and React

Node.js is required for the React/Vite development environment.

Verify:

```powershell
node --version
pnpm --version
```

Vite's current requirements should be checked in the official documentation:

[https://vite.dev/guide/](https://vite.dev/guide/)

Create the React application from the project root:

```powershell
pnpm create vite frontend --template react-ts
```

Then:

```powershell
cd frontend
pnpm install
```

Start the development server:

```powershell
pnpm dev
```

The terminal should provide a local URL similar to:

```text
http://localhost:5173/
```

Open it in a browser and verify that the React application works.

Stop the server with:

```text
Ctrl + C
```

Return to the project root:

```powershell
cd ..
```

---

# 16. VS Code Development Setup

During development, three terminals are useful.

### Terminal 1 — Python / Training

Used for:

- Dataset scripts
- Training
- Evaluation

### Terminal 2 — FastAPI

Used for:

```powershell
uvicorn app.main:app --reload
```

### Terminal 3 — React

Used for:

```powershell
cd frontend
pnpm dev
```

This separation makes it easier to monitor each part of the system.

---

---

# 32. FastAPI AI Service

After the model works independently, expose it through FastAPI.

Recommended structure:

```text
ai-service/
│
├── app/
│   ├── main.py
│   ├── inference.py
│   ├── preprocessing.py
│   └── schemas.py
│
├── training/
│   └── train.py
│
├── evaluation/
│   └── evaluate.py
│
├── tools/
│   └── audit_dataset.py
│
├── models/
│   └── tsl-resnet18.pth
│
└── requirements.txt
```

---

# 33. Running FastAPI

From the `ai-service` directory:

```powershell
uvicorn app.main:app --reload
```

The API should normally be available at:

`http://127.0.0.1:8000`

FastAPI provides interactive API documentation at:

`http://127.0.0.1:8000/docs`

Use this interface to test the prediction endpoint before connecting React.

---

# 35. React Interface

The initial interface should remain simple.

```text
+--------------------------------------+
| Tunisian Sign Language Recognition   |
|                                      |
|        [ Camera Preview ]            |
|                                      |
|          [ Recognize ]               |
|                                      |
| Prediction: XXXXX                    |
| Confidence: 94%                      |
|                                      |
+--------------------------------------+
```

---

# 36. React → FastAPI Communication

The communication flow is:

```text
React
  │
  │ POST /predict
  ▼
FastAPI
  │
  ▼
Image preprocessing
  │
  ▼
PyTorch model
  │
  ▼
Prediction
  │
  ▼
JSON response
  │
  ▼
React
```

Example response:

```json
{
  "label": "sign_name",
  "confidence": 0.94,
  "model_version": "resnet18-exp-001"
}
```

---

# 37. CORS

During development, React and FastAPI normally run on different ports.

For example:

```text
React:
http://localhost:5173

FastAPI:
http://localhost:8000
```

FastAPI therefore needs appropriate CORS configuration to allow the browser frontend to communicate with the backend.

---

# 44. Git Workflow

The `main` branch should contain stable work.

Example feature branches:

```text
main

feature/dataset-audit
feature/preprocessing
feature/resnet-baseline
feature/evaluation
feature/fastapi-inference
feature/react-interface
feature/realtime-inference
feature/browser-extension
```

Create a feature branch:

```powershell
git checkout -b feature/dataset-audit
```

After implementing and testing the feature:

```powershell
git add .
git commit -m "feat: add initial TSL dataset audit"
```

Merge the branch after verification.

---

# 45. Commit Convention

Use descriptive commit messages.

### Features

```text
feat: add dataset audit script
feat: add image preprocessing pipeline
feat: add ResNet18 training pipeline
feat: add FastAPI prediction endpoint
feat: add React camera interface
```

### Bug fixes

```text
fix: correct image normalization
fix: resolve FastAPI CORS configuration
fix: fix incorrect class mapping
```

### Documentation

```text
docs: update dataset documentation
docs: document training procedure
docs: update project architecture
```

---

# 46. `.gitignore`

Do not commit virtual environments, datasets, or large model files.

Recommended `.gitignore`:

```gitignore
.venv/

__pycache__/
*.py[cod]

node_modules/
dist/

*.pth
*.pt
*.onnx

data/original/
data/processed/

.env
.env.*

.vscode/
.idea/

.pytest_cache/
.mypy_cache/

.DS_Store
Thumbs.db
```

Large model artifacts can later be managed with Git LFS or a model registry if necessary.

---

 
