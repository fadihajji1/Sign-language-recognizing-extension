# Development, Contribution and Setup Guide

> **Legacy planning guide:** the live project folders have since been
> reorganized. Use the root [`README.md`](../README.md) for the current
> structure and [`setup.md`](../setup.md) for run commands.

## 1. Purpose of This Document

This document explains how to set up, develop, test, and contribute to the Tunisian Sign Language Recognition project.

It is written for developers who are comfortable with:

- VS Code
- Git
- JavaScript/TypeScript
- React
- General software development

but who may be new to:

- Deep Learning
- PyTorch
- Computer Vision
- Neural Network training
- Dataset preparation

The objective is to make the project reproducible from a completely fresh environment.

---

# 2. Project Overview

The project is a Deep Learning-based Tunisian Sign Language (TSL) recognition system.

The initial system recognizes **isolated signs from images**.

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

# 3. High-Level Architecture

The initial application consists of three main components:

```
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
│  57 initial classes         │
└─────────────────────────────┘
```

## 3.1 What is NOT required

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

---

# 4. Development Strategy

Development should follow these phases.

## Phase 1 — Environment

Install and verify:

- Git
- Python
- Node.js
- npm
- VS Code  


---

## Phase 2 — Project Structure

Create the repository and separate:

- frontend
- AI service
- datasets
- models
- experiments
- documentation  


---

## Phase 3 — Dataset

Start with the:

**First-ever Tunisian Sign Language Dataset**

Repository:

`W7CH/First-ever-Tunisian-Sign-Language-Dataset`

---

## Phase 4 — Dataset Audit

Before training a neural network, inspect the dataset.

The audit should determine:

- Number of images
- Number of classes
- Images per class
- Image dimensions
- Image formats
- Missing files
- Corrupted files
- Duplicate images
- Class imbalance
- Available signer/person information
- Lighting variations
- Background variations
- Hand orientation
- Label consistency

---

# 5. Recommended Project Structure

Create the project with the following structure:

```
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
│   │
│   ├── processed/
│   │
│   ├── splits/
│   │
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
└── CONTRIBUTION.md
```

---

# 6. Creating the Project From Scratch

Open PowerShell in VS Code.

Create the project:

```
mkdir tunisian-sign-language-ai
cd tunisian-sign-language-ai

# Initialize Git:

git init

# Create the main directories:

mkdir frontend
mkdir ai-service
mkdir data
mkdir models
mkdir docs
mkdir experiments

# Create dataset directories:

mkdir data\original
mkdir data\processed
mkdir data\splits
mkdir data\metadata

# Create AI service directories:

mkdir backend\app
mkdir ai-service\training
mkdir ai-service\evaluation
mkdir ml-pipeline\tools
mkdir ai-service\models
```

# 7. Python Installation

**Python** is required for:

- PyTorch
- Dataset processing
- Model training
- Model evaluation
- FastAPI
- Computer vision

Check the installed version:

```
python --version
```

**Python 3.11 or 3.12 is recommended for this project.**

If the command does not work, install Python and make sure :

- To add Python to system PATH

After installation, restart VS Code.

---

# 8. Create the Python Virtual Environment

A virtual environment keeps this project's Python dependencies isolated from other projects.

From the project root:

```
python -m venv .venv

# Activate it:

.\.venv\Scripts\Activate.ps1
```

The terminal should now display something similar to:

```
(.venv) PS C:\...\tunisian-sign-language-ai>
```

This means the virtual environment is active.

---

## 8.1 PowerShell Execution Policy Problem

If PowerShell displays an error preventing activation, run:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Then:

.\.venv\Scripts\Activate.ps1
```

The execution policy change only applies to the current PowerShell process.

---

# 9. Upgrade pip

With the virtual environment activated:

```
python -m pip install --upgrade pip
```

---

# 10. Install PyTorch

PyTorch is the main Deep Learning framework used by this project.

Do not blindly copy an old CUDA installation command from another tutorial.

Use the official PyTorch installation selector to choose the appropriate installation for the current machine.

Official documentation:

[https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

The appropriate installation depends on:

- Operating system
- Python version
- CPU/GPU
- NVIDIA CUDA support

A CPU installation is completely acceptable for starting the project.

---

# 11. Verify PyTorch

After installing PyTorch:

```
python

# Then:
import torch
print(torch.__version__)
print(torch.cuda.is_available())

# Exit Python:
exit()
```

If:

`torch.cuda.is_available()`

returns: `False`

that is not necessarily an error.

It simply means PyTorch cannot currently use a CUDA-compatible NVIDIA GPU.

The project can still run on CPU.

---

# 12. Install Remaining Python Dependencies

With the virtual environment active:

```
pip install fastapi
pip install uvicorn
pip install opencv-python
pip install numpy
pip install pandas
pip install scikit-learn
pip install matplotlib
pip install pillow
pip install tqdm
pip install torchvision
```

These packages provide:


| Package      | Purpose                                         |
| ------------ | ----------------------------------------------- |
| PyTorch      | Deep Learning                                   |
| torchvision  | Computer Vision utilities and pretrained models |
| FastAPI      | AI API                                          |
| Uvicorn      | FastAPI server                                  |
| OpenCV       | Image/video processing                          |
| NumPy        | Numerical operations                            |
| Pandas       | Dataset analysis                                |
| scikit-learn | Evaluation and metrics                          |
| Matplotlib   | Graphs and confusion matrices                   |
| Pillow       | Image processing                                |
| tqdm         | Progress bars                                   |


Save the dependencies:

```
pip freeze > ml-pipeline\requirements.txt
```

---

# 13. Optional Packages

These packages can be installed later when required.

For camera/hand processing:

```
pip install mediapipe
```

For experiment visualization:

```
pip install tensorboard
```

For experiment tracking:

```
pip install mlflow
```

Do not install every optional package immediately.

Only add dependencies when the project actually needs them.

---

# 14. Node.js

Node.js is required for the React development environment.

Check:

`node --version`

Check npm:

`npm --version`

Current Vite versions require a recent Node.js version. Before creating the frontend, verify the current requirement in the official Vite documentation:

[https://vite.dev/guide/](https://vite.dev/guide/)

---

# 15. Create the React Application

From the project root:

```
npm create vite@latest frontend -- --template react-ts
```

Then:

```
cd frontend
npm install

# Start the frontend:
npm run dev
```

Vite should display a local address similar to:

`http://localhost:5173/`

Open that address in the browser.

At this point, the React application should work independently.

---

---

---

# 16. Recommended VS Code Terminal Setup

During development, it is useful to have three terminals open.

## Terminal 1 — Training / Python

`(.venv)`

Used for:

- Dataset scripts
- Training
- Evaluation

---

## Terminal 2 — FastAPI

Used for:

`uvicorn app.main:app --reload`

---

## Terminal 3 — React

Used for:

`cd frontend`  
`npm run dev`

This makes the three parts of the system easy to monitor.

---

---

---

# 17. Understanding Deep Learning Before Training

Only a few concepts are required initially.

## Dataset

A dataset is the collection of examples used by the neural network.

In this project:

**Image → TSL sign label**

For example:

- image_001.jpg → sign_A
- image_002.jpg → sign_B
- image_003.jpg → sign_A

---

## Class

A class represents one recognizable sign.

The initial dataset contains 57 sign classes.

The model therefore needs to choose between:

Class 1  
Class 2  
...  
Class 57

---

## Model

The model is the neural network that learns visual patterns from images.

The initial recommended model is:

#### **ResNet18**

with transfer learning.

---

## Training

Training means showing the model examples and allowing it to adjust its internal parameters.

Conceptually:

```
Image
  ↓
Neural Network
  ↓
Prediction
  ↓
Compare prediction with correct label
  ↓
Calculate error
  ↓
Adjust model
  ↓
Repeat
```

---

## Epoch

One epoch means the model has processed the training dataset once.

For example:

```
Epoch 1
Epoch 2
Epoch 3
...
Epoch 20
```

---

## Batch

A batch is a small group of images processed together.

For example:

`Batch size = 32`

means the model processes 32 images at a time before updating its parameters.

---

## Learning Rate

The learning rate controls how strongly the model changes during training.

It is one of the most important training parameters.

---

# 18. Dataset Acquisition

Use the W7CH Tunisian Sign Language dataset as the starting dataset.

The original dataset should be placed under:

```
data/
└── original/
    └── w7ch/
```

Do not modify these original files.

The principle is:

```
Original Dataset
       │
       ▼
Audit
       │
       ▼
Preprocessing
       │
       ▼
Processed Dataset
```

The original dataset should remain reproducible and traceable.

---

# 19. Dataset Audit

Before training, create:

```
ml-pipeline/tools/audit_dataset.py
```

The script should eventually report:

```
Total images
Total classes
Images per class
Image dimensions
Image formats
Corrupted images
Potential duplicates
Missing labels
```

A useful first output could look like:

```
Dataset Audit
=============

Total images: 4423
Classes: 57

Minimum images/class: ...
Maximum images/class: ...
Average images/class: ...

Corrupted images: ...
Potential duplicates: ...
```

The exact numbers should always be generated from the downloaded dataset rather than manually assumed.

---

# 20. Dataset Preprocessing

The neural network should receive standardized images.

The initial preprocessing pipeline should include:

```
Original Image
      ↓
Read Image
      ↓
Convert to RGB
      ↓
Resize
      ↓
Normalize
      ↓
Tensor
      ↓
Model
```

The initial model can use:

```
224 × 224 RGB
```

because ResNet18 commonly operates on this image size.

---

# 21. Data Augmentation

Data augmentation creates controlled variations of training images.

Examples include:

- Small rotations
- Small translations
- Scaling
- Cropping
- Brightness changes
- Contrast changes  


However, augmentation must respect the characteristics of sign language.

Do not blindly apply horizontal flipping.

For some signs, left/right orientation can carry meaningful information.

Therefore every augmentation should have a reason.

---

# 22. Training / Validation / Test Split

The dataset should be divided into:

```
Dataset
   │
   ├── Training
   ├── Validation
   └── Testing
```

### Training

Used to learn model parameters.

### Validation

Used to make decisions during development.

### Testing

Used for final evaluation.

The test set should not be repeatedly used to make development decisions.

---

# 23. Signer-Aware Evaluation

If the dataset contains reliable signer/person identity, the preferred approach is to avoid putting the same person's examples into both training and testing.

For example:

```
Training:
Signer A
Signer B
Signer C
Signer D
Signer E

Validation:
Signer F

Testing:
Signer G
```

This tests whether the model can recognize signs performed by someone it has not seen during training.

If reliable signer identity is not available, this limitation must be documented.

Do not claim a signer-independent evaluation when the split does not support it.

---

# 24. Class Imbalance

The dataset may not contain the same number of images for every sign.

For example:

```
Class A → 300 images
Class B → 80 images
Class C → 150 images
```

This is called class imbalance.

Possible solutions include:

- Weighted loss
- Balanced sampling
- Controlled augmentation
- More data collection

The first approach should be measured rather than assumed to be optimal.

---

# 25. First Neural Network

The first recommended baseline is:

**ResNet18 + Transfer Learning**

The conceptual architecture is:

```
Input Image
   │
   ▼
224 × 224 × 3
   │
   ▼
ResNet18
   │
   ▼
Feature Extraction
   │
   ▼
Final Classification Layer
   │
   ▼
57 outputs
```

The final layer should be adapted to the number of classes in the actual prepared dataset.

---

# 26. Why ResNet18?

ResNet18 is a good first model because it is:

- Well known
- Relatively lightweight
- Easy to train
- Supported by torchvision
- Suitable for image classification
- Appropriate for a baseline experiment
- Easier to understand than a Transformer

The goal of the first experiment is not to build the most sophisticated possible model.

The goal is to establish a reliable baseline.

---

# 27. Transfer Learning

Instead of training the entire neural network from zero, use an existing pretrained model.

Conceptually:

```
ImageNet-pretrained ResNet18
             ↓
Replace classification layer
             ↓
Adapt to TSL classes
             ↓
Fine-tune
```

The pretrained network has already learned general visual features such as:

- edges
- textures
- shapes
- patterns

The project then adapts these features to Tunisian Sign Language.

---

# 28. First Training Experiment

The first experiment should be deliberately simple.

Example:

1. Model: ResNet18
2. Input: 224 × 224 RGB
3. Task: TSL image classification
4. Output: 57 classes
5. Optimizer: Adam
6. Loss: Cross Entropy
7. Epochs: Start with a small number
8. Batch size: Start with a reasonable value based on available memory
9. Random seed: Fixed

The exact hyperparameters should be recorded in the experiment configuration.

Do not change many parameters simultaneously.

---

# 29. Experiment Organization

Every meaningful experiment should have its own directory.

Example:

```
experiments/
└── exp-001-resnet18/
    ├── config.json
    ├── metrics.json
    ├── confusion_matrix.png
    └── model.pth
```

Record at least:

```
Dataset version
Dataset split
Model
Input size
Optimizer
Learning rate
Batch size
Epochs
Augmentation
Random seed
Training metrics
Validation metrics
Test metrics
```

This makes the research reproducible.

---

# 30. Important Evaluation Metrics

Do not report only accuracy.

The evaluation should eventually include:

- Accuracy
- Precision
- Recall
- Macro F1-score
- Per-class F1-score
- Confusion matrix
- Inference latency
- Model size  


The confusion matrix is particularly important because it shows which signs the model confuses.

---

# 31. Overfitting

A common Deep Learning problem is overfitting.

Example:

- **( train ) Training accuracy: 99%**
- **( test ) Validation accuracy: 70%**

This can indicate that the model has learned the training examples too specifically.

Possible causes include:

- Small dataset
- Similar images
- Background leakage
- Signer leakage
- Insufficient data diversity
- Excessive training
- Weak augmentation

Do not automatically solve overfitting by simply increasing the number of epochs.

---

---

---

# 32. FastAPI AI Service

After the first trained model works independently, expose it through FastAPI.

Recommended structure:

```
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

# 34. Running FastAPI

Activate the Python environment.

From:

ai-service/

run:

```
uvicorn app.main:app --reload
```

The API should normally be available at:

`http://127.0.0.1:8000`

 

FastAPI also provides interactive API documentation at:

`http://127.0.0.1:8000/docs`

Use this interface to test the prediction endpoint before connecting React.

---

# 35. Test the AI API Before React

This is an important development rule.

Do not immediately connect the camera.

First verify:

```
Image
  ↓
FastAPI
  ↓
Preprocessing
  ↓
PyTorch
  ↓
Prediction
```

For example:

```
{
  "label": "example_sign",
  "confidence": 0.94,
  "model_version": "resnet18-exp-001"
}
```

The exact label and confidence will depend on the trained model.

---

---

---

# 36. React Interface

The initial React interface should remain simple.

Suggested interface:

```
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

Do not initially build:

- Login page
- Dashboard
- User profiles
- Database
- History system
- Admin interface

These are outside the initial scope.

---

# 37. React → FastAPI Communication

The communication flow is:

```
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

```
{
  "label": "sign_name",
  "confidence": 0.94,
  "model_version": "resnet18-exp-001"
}
```

---

# 38. CORS

During development, React and FastAPI normally run on different ports.

For example:

- React: `http://localhost:5173`  
  
FastAPI: `http://localhost:8000`

The FastAPI application therefore needs appropriate CORS configuration so that the browser allows the frontend to communicate with the backend.

---

# 39. Start With One Image

Do not start with continuous camera recognition.

First implement:

```
Select/Capture Image
       ↓
Send Image
       ↓
Prediction
       ↓
Display Result
```

Only after this works should the project move toward continuous camera inference.

This makes debugging significantly easier.

---

# 40. Camera Recognition

The next stage is:

```
Camera
   ↓
Capture frame
   ↓
Preprocess
   ↓
Send to FastAPI
   ↓
Model inference
   ↓
Prediction
```

The system should not necessarily send every camera frame to the server.

A controlled frame-sampling strategy can be used.

For example:

```
Camera: 30 FPS

Inference:
5–10 FPS
```

The exact value must be determined experimentally.

---

# 41. Real-Time Recognition

A system should not be called "real-time" simply because it uses a webcam.

Measure:

- Inference latency
- Requests per second
- Camera FPS
- Model loading time
- Network latency
- CPU/GPU usage  


Eventually:

```
Total latency =
capture
+ preprocessing
+ network
+ inference
+ response
+ rendering
```

These measurements should be documented.

---

# 42. Temporal Recognition

The initial project focuses on isolated signs.

However, real sign-language communication can contain sequences of movements.

A future architecture can therefore be:

```
Video
  ↓
Frame extraction
  ↓
Spatial feature extraction
  ↓
Temporal model
  ↓
Sign sequence
  ↓
Text
```

Possible future models include:

- LSTM
- GRU
- Temporal CNN
- Transformer

These should be investigated only after the image-based baseline is working.

---

---

---

---

---

# 43. Browser Extension

The browser extension should be implemented at the final stage.

The recommended order is:

```
Standalone AI application
          ↓
Validated model
          ↓
Working API
          ↓
Camera recognition
          ↓
Performance evaluation
          ↓
Browser extension
```

The extension should reuse the validated recognition system rather than becoming the first place where the AI model is tested.

---

# 45. Git Workflow

The main branch should contain stable work.

Example feature branches:

```
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

Create a branch:

```
git checkout -b feature/dataset-audit
git add .
git commit -m "feat: add initial TSL dataset audit"
```

Use descriptive commit messages.

```
feat: add dataset audit script
feat: add image preprocessing pipeline
feat: add ResNet18 training pipeline
feat: add FastAPI prediction endpoint
feat: add React camera interface
```

Then merge the branch into the main development branch after verification.

---

# 47. .gitignore

The repository should not commit virtual environments, datasets, or large model files.

Recommended `.gitignore`:

```
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

# 48. Documentation Rule

Every significant project change should be documented.

Documentation should be updated when:

- Architecture changes
- Dataset processing changes
- Model changes
- API changes
- Frontend behavior changes
- Development instructions change
- Research methodology changes  


The project should maintain a changelog:

```
CHANGELOG.md
```

Each implemented project change should be recorded there.

---

---

---

---

---

# 51. Run Workflow

If starting this project completely from zero, follow these steps in order.

## Step 1 — Install software

Install:

```
Git
Python
Node.js
VS Code
```

---

## Step 2 — Create repository

```
mkdir tunisian-sign-language-ai
cd tunisian-sign-language-ai
git init
```

---

## Step 3 — Create virtual environment

```
python -m venv .venv
```

Activate:

.\.venv\Scripts\Activate.ps1

---

## Step 4 — Upgrade pip

```
python -m pip install --upgrade pip
```

---

## Step 5 — Install PyTorch

Use the official PyTorch installation selector:

`https://pytorch.org/get-started/locally/`

---

## Step 6 — Verify PyTorch

```
python
```

Then:

```
# run this file
import torch
print(torch.__version__)
print(torch.cuda.is_available())

# Then:
exit()
```

---

## Step 7 — Install the remaining Python dependencies

```
pip install fastapi uvicorn opencv-python numpy pandas scikit-learn matplotlib pillow tqdm torchvision
```

---

## Step 8 — Save dependencies

```
pip freeze > ml-pipeline\requirements.txt
```

---

## Step 9 — Create the React application

From the project root:

```
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm run dev
```

Verify the React application opens in the browser.

---

## Step 10 — Download the TSL dataset

Place the original dataset under:

```
data/original/w7ch/
```

Do not modify it.

---

## Step 11 — Perform the dataset audit

Create and run:

`ml-pipeline/tools/audit_dataset.py`

Do not train the model yet.

---

## Step 13 — Document the audit

Record:

- Number of images
- Number of classes
- Distribution
- Image dimensions
- Potential duplicates
- Corrupted files
- Signer information
- Dataset limitations  


---

## Step 14 — Prepare the processed dataset

Create:

`data/processed/`  
`data/splits/`

The processed dataset should be generated from the original dataset.

---

## Step 15 — Train the first model

Use:

`ResNet18`

as the initial baseline.

---

## Step 16 — Evaluate

Generate:

```
Accuracy
Precision
Recall
Macro F1
Per-class F1
Confusion matrix
```

---

## Step 17 — Save the model

Example:

```
models/
└── tsl-resnet18-exp-001.pth
```

---

## Step 18 — Build FastAPI inference

Load the trained model and expose:

```
POST /predict
```

---

## Step 19 — Test FastAPI independently

Use:

`http://localhost:8000/docs`

and verify image prediction.

---

## Step 20 — Connect React

Implement:

```
React
   ↓
POST /predict
   ↓
FastAPI
   ↓
PyTorch
   ↓
Prediction
   ↓
React
```

---

## Step 21 — Add camera

Only after image prediction works.

---

## Step 22 — Measure performance

Measure:

```
Inference latency
FPS
Prediction stability
CPU/GPU usage
```

---

## Step 23 — Improve the model

Only after establishing a baseline.

Possible improvements:

- Better preprocessing
- Better augmentation
- Class balancing
- Hyperparameter tuning
- Fine-tuning strategy
- Different CNN architectures
- More data  


---

## Step 24 — Investigate temporal recognition

Only after isolated sign recognition is sufficiently reliable.

---

## Step 25 — Browser extension

The browser extension is the final deployment-oriented stage.

---

---

---

---

# 54. Final Development Philosophy

The project should not begin by trying to build a complete browser extension.

The correct progression is:

```

```

```
                    RESEARCH
                       │
                       ▼
                 Dataset Audit
                       │
                       ▼
                  Preprocessing
                       │
                       ▼
                 CNN Baseline
                       │
                       ▼
                    Training
                       │
                       ▼
                   Evaluation
                       │
                       ▼
                Error Analysis
                       │
                       ▼
                Improved Model
                       │
                       ▼
                  FastAPI API
                       │
                       ▼
                 React Interface
                       │
                       ▼
                  Camera Input
                       │
                       ▼
              Real-Time Recognition
                       │
                       ▼
              Browser Extension
```

The browser extension is therefore the final deployment target, not the starting point.

The initial academic contribution is the development and evaluation of a Deep Learning system for isolated Tunisian Sign Language recognition using the selected dataset.
