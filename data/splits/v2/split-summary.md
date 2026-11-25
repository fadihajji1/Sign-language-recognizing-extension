# Split Generation Report

- Eligible images: **4423**
- Classes: **57**
- Train: **3096**
- Validation: **663**
- Test: **664**
- Exact duplicate hash leaks: **0**

## Per-class counts

| Class | Unique hash groups | Train | Validation | Test |
|---|---:|---:|---:|---:|
| `3aslema` | 51 | 36 | 8 | 7 |
| `3ayla` | 81 | 57 | 12 | 12 |
| `5adamet` | 28 | 20 | 4 | 4 |
| `5al-3am` | 191 | 134 | 29 | 28 |
| `5mis` | 54 | 38 | 8 | 8 |
| `5ou` | 182 | 130 | 28 | 28 |
| `a7ad` | 39 | 27 | 6 | 6 |
| `assam` | 35 | 24 | 5 | 6 |
| `baladya` | 109 | 76 | 16 | 17 |
| `banka` | 87 | 61 | 13 | 13 |
| `barnamjk` | 91 | 64 | 14 | 13 |
| `bent` | 224 | 157 | 34 | 33 |
| `bou` | 138 | 97 | 21 | 20 |
| `bousta` | 50 | 35 | 8 | 7 |
| `car` | 33 | 23 | 5 | 5 |
| `chabeb` | 53 | 37 | 8 | 8 |
| `cv` | 56 | 39 | 8 | 9 |
| `dar` | 79 | 55 | 12 | 12 |
| `demande` | 34 | 24 | 5 | 5 |
| `eben` | 164 | 115 | 25 | 24 |
| `enti` | 57 | 40 | 9 | 8 |
| `erb3a` | 66 | 46 | 10 | 10 |
| `jad` | 172 | 120 | 26 | 26 |
| `jadda` | 154 | 108 | 23 | 23 |
| `jom3a` | 56 | 39 | 8 | 9 |
| `karhba` | 27 | 19 | 4 | 4 |
| `labes` | 21 | 15 | 3 | 3 |
| `louage` | 35 | 27 | 5 | 6 |
| `lyoum` | 50 | 35 | 8 | 7 |
| `ma7kma` | 44 | 31 | 7 | 6 |
| `mar2a` | 143 | 100 | 21 | 22 |
| `mar7ba` | 15 | 10 | 2 | 3 |
| `mostawsaf` | 111 | 78 | 17 | 16 |
| `métro` | 52 | 36 | 8 | 8 |
| `n3awnek` | 87 | 61 | 13 | 13 |
| `nekteblk` | 56 | 39 | 8 | 9 |
| `non` | 78 | 55 | 12 | 11 |
| `o5t` | 161 | 113 | 24 | 24 |
| `om` | 46 | 32 | 7 | 7 |
| `oui` | 94 | 66 | 14 | 14 |
| `radio` | 120 | 84 | 18 | 18 |
| `sbitar` | 47 | 33 | 7 | 7 |
| `se7a` | 118 | 83 | 18 | 17 |
| `sebt` | 36 | 25 | 5 | 6 |
| `siye7a` | 64 | 45 | 10 | 9 |
| `t7eb` | 35 | 30 | 7 | 8 |
| `ta3lim` | 76 | 53 | 11 | 12 |
| `ta3raf` | 32 | 22 | 5 | 5 |
| `ta9ra` | 39 | 27 | 6 | 6 |
| `taxi` | 96 | 67 | 14 | 15 |
| `telvza` | 30 | 21 | 4 | 5 |
| `tfol` | 88 | 62 | 13 | 13 |
| `tha9afa` | 70 | 49 | 10 | 11 |
| `thleth` | 67 | 47 | 10 | 10 |
| `thnin` | 47 | 33 | 7 | 7 |
| `train` | 56 | 39 | 8 | 9 |
| `wzara` | 81 | 57 | 12 | 12 |

## Warnings
- Class labels are inferred from the first folder below data-dir; verify this matches the official dataset layout.
- Root-level images are excluded because their class label is unverified.
- Identical file contents are kept in the same split; visually identical re-encodings are not detected.
- Signer IDs are unavailable, so this is not signer-independent evaluation.
- Classes with fewer than three unique hash groups cannot be represented in all three splits.

## Excluded files / issues
- `interfaces.png`: root-level image has no verified class label; excluded
