"""Model construction helpers shared by training and evaluation."""

from torch import nn
from torchvision.models import mobilenet_v3_small, resnet18


def build_model(architecture, num_classes):
    if architecture in ("resnet18", "torchvision.models.resnet18"):
        model = resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if architecture == "mobilenet_v3_small":
        model = mobilenet_v3_small(weights=None)
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
        return model
    raise ValueError(f"Unsupported architecture: {architecture}")
