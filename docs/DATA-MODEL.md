# DATA-MODEL.md

# Data and ML Model Specification

## 1. Important Clarification

This project does not require an application database.

Therefore, this document describes:

1. the machine-learning dataset
2. dataset metadata
3. class labels
4. model input/output
5. inference data structures

A PostgreSQL user/application data model is intentionally excluded.

## 2. Source Dataset

### W7CH First-ever Tunisian Sign Language Dataset

According to the GitHub repository:

```text
Images:       4,423
Signs:        57
People:       7
Resolution:   224 × 224
Categories:   5
```

Categories:

```text
Demandes
Destinations
Famille
Jours
Transport
```

The number of images differs between classes. citeturn1view0

## 3. Dataset Lifecycle

```text
Original
   ↓
Audit
   ↓
Cleaned
   ↓
Processed
   ↓
Augmented training data
   ↓
Train / Validation / Test
```

Only the training set receives training augmentation.

## 4. Dataset Directory

Recommended:

```text
data/
├── original/
│   └── w7ch/
├── processed/
│   └── v1/
├── splits/
│   ├── train/
│   ├── validation/
│   └── test/
└── metadata/
    ├── classes.json
    ├── dataset.json
    └── preprocessing.json
```

## 5. Class Metadata

Example:

```json
{
  "class_id": 0,
  "label": "<actual dataset label>",
  "category": "Demandes"
}
```

Do not manually invent translations for class names.

The original folder labels should be preserved and a separate translation mapping can be created when linguistically validated.

## 6. Dataset Metadata

Recommended:

```json
{
  "dataset_name": "W7CH Tunisian Sign Language",
  "version": "1.0-source",
  "image_count": 4423,
  "class_count": 57,
  "image_size": [224, 224],
  "source": "W7CH GitHub repository",
  "license_source": "repository LICENSE"
}
```

## 7. Derived Dataset Version

Example:

```json
{
  "dataset_name": "TSL-Academic-Derived",
  "version": "1.0",
  "source_dataset": "W7CH-v1",
  "preprocessing": "resize-normalize",
  "augmentation": [
    "small_rotation",
    "translation",
    "brightness",
    "contrast"
  ],
  "split_strategy": "documented"
}
```

## 8. Training Sample

Conceptual structure:

```text
TrainingSample
--------------
image_path
class_id
class_label
split
augmentation_applied
source_image_id
```

## 9. Model Input

Initial model:

```text
Input:
RGB image
Size:
224 × 224 × 3
```

The exact input size may be changed for an experimental architecture, but the change must be recorded.

## 10. Model Output

The classifier returns a vector of 57 class probabilities:

```text
P(class_1)
P(class_2)
...
P(class_57)
```

The final prediction is:

```text
argmax(probabilities)
```

## 11. Inference Object

Example:

```json
{
  "label": "<dataset-label>",
  "confidence": 0.94,
  "model_version": "tsl-cnn-v1.0.0"
}
```

## 12. Training Metadata

Every experiment should record:

```text
experiment_id
dataset_version
model_architecture
input_size
batch_size
learning_rate
optimizer
epochs
augmentation
random_seed
train_metrics
validation_metrics
test_metrics
```

## 13. Evaluation Data

Recommended output:

```text
metrics/
├── accuracy.json
├── precision_recall_f1.json
├── confusion_matrix.png
└── classification_report.txt
```

## 14. Future Video Data Model

When dynamic recognition is investigated:

```text
Sequence
--------
sequence_id
sign_label
signer_id
video_path
fps
frame_count
resolution
capture_conditions
```

The current W7CH image dataset should not be falsely represented as a sequence dataset.

## 15. Dataset Integrity

The original dataset should be immutable.

Use checksums if practical:

```text
original image
      ↓
SHA-256
      ↓
metadata record
```

This makes experiments reproducible.

## 16. License Documentation

The W7CH GitHub repository currently displays a CC0-1.0 license. citeturn1view0

A separate Mendeley record for the same dataset currently displays CC BY 4.0. citeturn0search6

Because these records disagree, the project should:

- preserve the source attribution
- cite the W7CH authors
- cite the original repository
- record the exact source used
- avoid asserting a single license for all copies without resolving the discrepancy

## 17. Academic Dataset Principle

The project must distinguish:

```text
Source dataset
       ≠
Processed dataset
       ≠
Augmented training dataset
       ≠
Model
```

This distinction is important for a reproducible academic project.
