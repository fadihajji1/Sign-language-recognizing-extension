# Implementation starter

Start with `implementation/STEP-BY-STEP-IMPLEMENTATION.md`.

The first executable task is Phase 1, the read-only dataset audit. It requires Python and Pillow. From this directory, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r ml-pipeline/requirements-audit.txt
python ml-pipeline/tools/audit_dataset.py --data-dir data/original/w7ch --output-dir data/metadata/audit-v1
```

Download and extract the W7CH dataset into `data/original/w7ch/` before running the audit. The script never edits the source images. Review `dataset-audit.md` before training.
