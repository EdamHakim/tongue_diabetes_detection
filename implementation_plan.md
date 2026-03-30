# Update T2DM Tongue Detection Notebook to Match Actual Dataset

## Problem Summary

The notebook was written with **assumptions** about the dataset structure that don't match the **actual data**. Additionally, 5 code cells are **corrupted** (character-per-line encoding). This plan addresses all mismatches and fixes the notebook.

---

## Findings from Verification

### 1. Folder Structure ❌ Mismatch

| Property | Notebook Assumes | Actual Data |
|---|---|---|
| Root path | `/kaggle/input/tongue_diabetes_dataset` | `data/preprocessedcropped/` |
| Layout | Flat: `diabetic/`, `non_diabetic/` | Pre-split: `train/`, `valid/`, `test/` |
| Class names | `diabetic`, `non_diabetic` | `diabetes`, `nondiabetes` |
| Splitting | Manual 70/15/15 patient-level split | **Already split** by dataset authors |

### 2. Filename Convention ❌ Mismatch

| Property | Notebook Assumes | Actual Data |
|---|---|---|
| Pattern | `P{id}_{shot}.jpg` (5 shots/patient) | `r_d_(ID)_augtype.jpg` / `r_nd_(ID)_augtype.jpg` |
| Patient grouping | 5 images = 1 patient | ID in parentheses **is** the patient ID |
| Augmentation | None assumed (raw images) | Train/valid already augmented: `_flip`, `_resized`, `_rotate_45`, `_rotate_90`, `_rotate_neg_45`, `_rotate_neg_90` (6 variants per patient) |
| Test images | Same format | Original images, no augmentation suffix: `r_d_(173).jpg` |

### 3. Image Resolution ⚠️ Mixed

| Split | Resolution | Notes |
|---|---|---|
| Train | 300×300 (100%) | All uniformly preprocessed |
| Valid | 300×300 (100%) | All uniformly preprocessed |
| Test | **Wildly variable** (214×273 to 2572×2495) | Raw unprocessed images — **all 50 test images are non-300×300** |

### 4. Dataset Counts

| Split | diabetes | nondiabetes | Total |
|---|---|---|---|
| Train | 1,050 (175 patients × 6 aug) | 1,050 (175 patients × 6 aug) | 2,100 |
| Valid | 300 (50 patients × 6 aug) | 300 (50 patients × 6 aug) | 600 |
| Test | 25 (25 patients × 1 orig) | 25 (25 patients × 1 orig) | 50 |
| **Total** | 1,375 | 1,375 | **2,750** |

### 5. Patient Leakage Check

- Train ∩ Valid: **0 overlap** ✅
- Train ∩ Test: **1 overlap** (patient ID 179 in `diabetes`) ⚠️
- Valid ∩ Test: **0 overlap** ✅

### 6. Corrupted Cells

Cells 16, 21, 25, 28, 30 have **character-per-line encoding** (each character is a separate `source` line). These need to be rewritten with proper line-based encoding.

---

## Proposed Changes

### [MODIFY] [t2dm_tongue_detection.ipynb](file:///d:/Everything/ESPRIT/3IA/2eme%20semestre/AI%20Project/Investigate%20Phase/datasets/t2dm_tongue_detection/t2dm_tongue_detection.ipynb)

Since 5 cells are corrupted and the notebook has fundamental assumptions that don't match the data, the most reliable approach is to **regenerate the notebook via Python script**, preserving all working cells and fixing the issues.

#### Changes by section:

1. **Cell 0 (Markdown header)**: Update dataset summary table to reflect actual structure:
   - Folder structure: `train/valid/test` each with `diabetes/` and `nondiabetes/`
   - Filename convention: `r_d_(ID)_augtype.jpg` / `r_nd_(ID)_augtype.jpg`
   - Image resolution: 300×300 (train/valid), variable (test)
   - Total images: 2,750
   - Data already pre-split and augmented

2. **Cell 5 (Paths & EDA)**: Update `DATA_ROOT`, `CLASS_DIRS`, `LABEL_MAP` to match actual paths (`data/preprocessedcropped/`) and class names (`diabetes`, `nondiabetes`)

3. **Cell 10 (Markdown - patient split)**: Update to note data is pre-split; adjust patient ID extraction description

4. **Cell 11-12 (Patient-level split code)**: Replace with code that **uses the existing split** rather than re-splitting. Extract patient IDs from filenames using regex `r_(?:d|nd)_\((\d+)\)`. Still verify no patient leakage across splits.

5. **Cell 16 (Dataset & DataLoaders) — CORRUPTED**: Rewrite with proper encoding. Update to use the pre-split data directly instead of `df_sorted['split']`

6. **Cell 21 (Training loop) — CORRUPTED**: Rewrite with proper encoding. Preserve the 3-phase training logic.

7. **Cell 25 (Test evaluation) — CORRUPTED**: Rewrite with proper encoding.

8. **Cell 28 (Grad-CAM) — CORRUPTED**: Rewrite with proper encoding.

9. **Cell 30 (Cross-validation) — CORRUPTED**: Rewrite with proper encoding.

> [!IMPORTANT]  
> The train/valid sets contain **pre-augmented** images (6 variants per patient). The notebook's own augmentation pipeline (Section 4) will apply **additional** augmentations on top. This is fine, but worth noting—the effective augmentation is stacked.
/// not need for additional augmentation
> [!WARNING]
> There is **1 patient ID overlap** (ID 179) between train and test in the `diabetes` class. This is a minor issue in the original dataset. The notebook will log this finding but proceed since we're using the dataset's own split.

---

## Open Questions

> [!IMPORTANT]
> **DATA_ROOT path for Kaggle**: Should the notebook use a relative path (`./data/preprocessedcropped`) for local testing, or the Kaggle path (`/kaggle/input/...`)? I'll default to making it **auto-detect** (check Kaggle first, fall back to local).
///kaggle/input/datasets/edamhakim/tongue-diabetes-dataset
---

## Verification Plan

### Automated Tests
- Run a Python script to validate the regenerated notebook is valid JSON with no corrupted cells
- Verify all cell sources are properly line-encoded (no single-character lines)
- Check that all path references match the actual dataset structure

### Manual Verification  
- User uploads the notebook to Kaggle and runs it end-to-end
