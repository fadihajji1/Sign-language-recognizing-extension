# Explanation

explain several files for better understanding

---

## audit_dataset vs create_splits

These are two separate tools for preparing and checking an image dataset:

### audit_dataset.py

audit_dataset.py — inspect the dataset:

This scans image files in the dataset folder and reports which are readable, their dimensions and formats, and which files have identical contents. It does not move, rename, resize, or delete the original images.

It creates these files in the required --output-dir:


| file                  | purpose                                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| images.csv            | one row per image, with its path, inferred label, dimensions, format, content hash, and whether it could be read. |
| class_counts.csv      | number of readable images for each inferred label.                                                                |
| unreadable_images.csv | images that could not be opened, with the error.                                                                  |
| exact_duplicates.json | groups of files with identical contents.                                                                          |
| dataset-audit.json    | machine-readable summary of the scan.                                                                             |
| dataset-audit.md      | human-readable report with counts and limitations.                                                                |



The label is inferred from the image’s immediate parent folder, so review the report if the dataset has nested folders.

### create_splits

create_splits.py — prepare data for model training
This selects eligible images and assigns them to training, validation, and test groups. By default, the proportions are 70%, 15%, and 15%. A fixed random seed makes the assignment reproducible. Images with identical file contents are kept together where possible.

It expects images to follow this folder structure:

It creates these files in --output-dir (default: data/splits/v1):


| file                                        | purpose                                                                                                                                            |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| train.csv, val.csv, test.csv                | lists of images assigned to each group, including their relative paths, labels, dimensions, and hashes. The images themselves stay where they are. |
| split-summary.json                          | machine-readable counts, exclusions, warnings, and per-class totals.                                                                               |
| [split-summary.md](http://split-summary.md) | human-readable report, including excluded files and any detected duplicate-hash leaks.                                                             |


In short: run the audit tool to understand and check the dataset; run the split tool to create CSV lists for training and evaluation. Both write reports outside the source dataset and leave the original images unchanged.

---

## Explanation of `tsl_data.py`

## 1. What is this file for?

The file `ml-pipeline/src/tsl_data.py` prepares the Tunisian Sign Language (TSL) image dataset so that a deep learning model can use it.

Its main responsibilities are:

1. Find the dataset and split CSV files.
2. Read images and their corresponding sign labels.
3. Apply image transformations.
4. Convert images into PyTorch tensors.
5. Organize images into batches.
6. Provide separate DataLoaders for training, validation, and testing.

**Important:** This file does not train a model, recognize signs, or open the webcam. It prepares the data required for those later steps.

---

## 2. Project paths and configuration

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "original" / "w7ch"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits" / "v2"

IMAGE_SIZE = 224
```

These variables tell Python where to find the project files.

- PROJECT_ROOT: identifies the root directory of the project.
- DATA_DIR: points to the original TSL images.
- SPLITS_DIR: points to the CSV files created during the dataset-splitting phase.
- IMAGE_SIZE: defines the dimensions expected by our model: 224 × 224 pixels.
Using paths relative to the project root makes the code easier to move between computers.

3. Image normalization

```Python
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
```

Neural networks generally work better when image values are normalized.

These values are the standard ImageNet normalization parameters. They are commonly used when training ResNet models initialized with ImageNet-pretrained weights.

Normalization adjusts the pixel values into a range and distribution suitable for the model.

4. Image transformations

The function get_transforms() defines the operations applied to images before they enter the model.

```Python
def get_transforms(training=False):
```

It accepts a parameter called training.

- If training=True, it applies data augmentation.
- If training=False, it only applies the standard transformations.
Data augmentation

```Python
if training:
    operations.extend([
        transforms.RandomAffine(
            degrees=5,
            translate=(0.03, 0.03),
        ),
        transforms.ColorJitter(
            brightness=0.10,
            contrast=0.10,
        ),
    ])
```

Data augmentation creates slightly modified versions of training images.

This helps the model become more robust to small variations.

We use:

- RandomAffine: applies small rotations and translations.
- ColorJitter: makes small changes to brightness and contrast.
We deliberately avoid horizontal flipping because mirroring a sign could change its meaning.

Augmentation is applied only to training images, not validation or test images.
Resizing and normalization

```Python
operations.extend([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])
```

These operations:

1. Resize the image to 224 × 224 pixels.
2. Convert it into a PyTorch tensor.
3. Normalize its pixel values.

The model will therefore receive images in a consistent format.

5. The TSLImageDataset class

```Python
class TSLImageDataset(Dataset):
```

This class represents our TSL image dataset in a format that PyTorch understands.

It inherits from Dataset, a PyTorch class used to represent collections of training examples.

Each example contains:

- An image.
- The numerical ID corresponding to its sign label.
The constructor

```Python
def __init__(self, csv_path, data_dir, class_to_idx, training=False):
```

The constructor receives four parameters:


| Parameter    | Purpose                                      |
| ------------ | -------------------------------------------- |
| csv_path     | Location of the CSV manifest                 |
| data_dir     | Location of the original images              |
| class_to_idx | Mapping between sign names and numerical IDs |
| training     | Determines whether augmentation is enabled   |


The constructor reads the CSV file:

```
self.records = pd.read_csv(self.csv_path, encoding="utf-8-sig")
```

It then checks that:

- The CSV exists.
- Required columns are present.
- The CSV contains records.
- Labels are not missing.
- Every label belongs to the known class mapping.
- Image paths actually exist.  
  
These checks help detect dataset problems before training starts.  
The **len**() method  
def **len**(self):    return len(self.records)

This returns the number of images in the dataset.

Our current split contains:
Split	Images
Training	3,096
Validation	663
Testing	664
Total	4,423

The **getitem**() method
def **getitem**(self, index):

This method retrieves one image and its label.

First, it retrieves the corresponding CSV record:
```
row = self.records.iloc[index]
```

Then it builds the image path and gets the sign label:

```
image_path = self.data_dir / str(row["relative_path"])
label_name = row["label"]
```

The image is opened and converted to RGB:
with Image.open(image_path) as image:    image = image.convert("RGB")    

```
image_tensor = self.transform(image)
```

Finally, the text label is converted into a numerical ID:

```
label_id = self.class_to_idx[label_name]
```

For example, a class mapping could look like this:
Sign label	|Numerical ID|
------------|------------|
bonjour     |	0        |
merci       |	1        |
métro       |	2        |
taxi        |	3        |

The actual mapping is generated automatically from the dataset's class names.

The method returns:
return image_tensor, torch.tensor(label_id, dtype=torch.long)

This gives PyTorch the image tensor and its corresponding numerical label.

6. Creating the DataLoaders

```
def create_dataloaders(batch_size=32, num_workers=0):
```

This function creates three datasets:

- Training dataset.
- Validation dataset.
- Testing dataset.
It reads the three CSV files:

```
csv_paths = {"train": SPLITS_DIR / "train.csv",
            "val": SPLITS_DIR / "val.csv",    
            "test": SPLITS_DIR / "test.csv",
            }
```

Creating the class mapping

```
all_labels = set()
```

The function collects the labels from all three CSV files.

It then creates a sorted list:

```
class_names = sorted(all_labels)
```

And assigns a numerical ID to every class:

```
class_to_idx = {
    class_name: index for index, 
    class_name in enumerate(class_names)
    }
```

We verify that the dataset contains exactly 57 classes:

```
if len(class_to_idx) != 57:
```

This is important because our model must eventually predict one of 57 possible sign classes.
Creating the datasets


```
datasets = {
"train": TSLImageDataset(csv_paths["train"], DATA_DIR, class_to_idx, training=True),    
"val": TSLImageDataset(csv_paths["val"], DATA_DIR, class_to_idx training=False),    
"test": TSLImageDataset(csv_paths["test"], DATA_DIR, class_to_idx, training=False),
}
```


Notice that augmentation is enabled only for training.


This prevents validation and test images from being artificially modified.
Creating the DataLoaders

```
loaders = {
    "train": DataLoader(datasets["train"], batch_size=batch_size, shuffle=True, num_workers=num_workers,),    
    "val": DataLoader(datasets["val"], batch_size=batch_size, shuffle=False, num_workers=num_workers,),    
    "test": DataLoader(datasets["test"], batch_size=batch_size, shuffle=False, num_workers=num_workers,),
    }
```
A DataLoader groups images into batches.

For example, with:

```
batch_size=32
```

the model receives 32 images at a time instead of processing all 3,096 training images simultaneously.

The training DataLoader uses:

```
shuffle=True
```

This randomizes the order of training images between epochs.

Validation and testing use:

```
shuffle=False
```

because their order does not need to be randomized.