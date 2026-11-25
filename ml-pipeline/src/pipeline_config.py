"""Shared pipeline configuration loading."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"


def load_config():
    with CONFIG_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def project_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path
