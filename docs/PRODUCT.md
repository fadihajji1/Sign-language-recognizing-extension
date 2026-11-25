# PRODUCT.md

# Product Requirements and Specifications

## 1. Product Name

**Tunisian Sign Language AI Recognition System**

## 2. Product Type

Academic AI/computer-vision project with a future browser-extension deployment target.

## 3. Product Vision

Create a lightweight AI system capable of recognizing supported Tunisian Sign Language signs and presenting their meaning through a simple interface.

The final system may be integrated into a browser extension to assist communication during online meetings.

## 4. Problem Statement

People who do not understand Tunisian Sign Language may have difficulty communicating with TSL users.

Most existing sign-language recognition research focuses on better-resourced sign languages. A TSL-specific system provides an opportunity to study recognition using locally relevant data.

## 5. Primary Objective

Develop and experimentally evaluate a neural network for isolated Tunisian Sign Language recognition.

## 6. Secondary Objectives

- Build a simple camera-based interface.
- Expose model inference through an API.
- Compare neural-network architectures.
- Measure model accuracy and generalization.
- Measure real-time inference performance.
- Prepare an architecture that can later support dynamic signs.
- Prepare the application for future browser-extension integration.

## 7. Target Users

The prototype is intended for:

- academic researchers
- students
- developers
- TSL learners
- people experimenting with accessibility technology
- future TSL users in online meetings

The MVP is not intended to be presented as a certified professional interpreter.

## 8. Functional Requirements

### FR-01 — Camera Access

The interface shall request permission to access the user's camera.

### FR-02 — Image/Frame Capture

The application shall capture an image or camera frame for recognition.

### FR-03 — Prediction

The AI service shall return the most probable supported TSL sign.

### FR-04 — Confidence

The inference response shall include a confidence score.

### FR-05 — Result Display

The React interface shall display:

- predicted sign
- confidence
- recognition status

### FR-06 — Low Confidence

The interface shall indicate when the model confidence is below the configured threshold.

### FR-07 — Model Information

The application should expose the model name/version used for the prediction.

### FR-08 — Real-Time Mode

The system should support repeated frame inference after the basic single-frame workflow is validated.

### FR-09 — Future Extension

The architecture shall permit a browser extension to communicate with the same recognition service.

## 9. Explicitly Excluded

The initial product shall not include:

- login
- registration
- user accounts
- authentication
- authorization
- user management
- PostgreSQL
- recognition history
- administrative dashboards
- payment
- multi-tenancy
- Node.js backend API

These would add complexity without contributing to the academic ML objective.

## 10. Non-Functional Requirements

### NFR-01 — Responsiveness

The interface should remain responsive during inference.

### NFR-02 — Performance

The model should be benchmarked for inference latency and FPS.

### NFR-03 — Reproducibility

Training must use documented:

- dataset version
- preprocessing
- augmentation
- train/validation/test split
- model architecture
- hyperparameters
- random seed

### NFR-04 — Privacy

Camera frames should not be stored by default.

### NFR-05 — Maintainability

The React interface and Python AI service should remain independently testable.

### NFR-06 — Extensibility

The inference API should be reusable by a future browser extension.

## 11. MVP Acceptance Criteria

The MVP is complete when:

1. The W7CH dataset is audited.
2. A reproducible training pipeline exists.
3. At least one CNN baseline is trained.
4. Test metrics are reported.
5. The model can perform inference through FastAPI.
6. React can send an input frame to FastAPI.
7. React displays the prediction.
8. Confidence is displayed.
9. Inference latency is measured.
10. Limitations are documented.

## 12. Research Evaluation

Minimum metrics:

- accuracy
- precision
- recall
- macro F1
- per-class F1
- confusion matrix
- inference latency

Where feasible:

- signer-independent test
- top-k accuracy
- FPS
- robustness under lighting/background changes

## 13. Future Product Evolution

### Version 1
Static/isolated sign recognition.

### Version 2
Real-time camera recognition.

### Version 3
Dynamic sign recognition from video sequences.

### Version 4
Continuous sign sequence recognition.

### Version 5
TSL-to-Arabic/French/English translation.

### Version 6
Speech output.

### Version 7
Browser-extension integration for online meetings.
