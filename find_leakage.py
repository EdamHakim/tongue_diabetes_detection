import pandas as pd
import re
from pathlib import Path

# Paths
DATA_ROOT = Path('data/preprocessedcropped')
SPLITS = ['train', 'valid', 'test']
CLASSES = ['diabetes', 'nondiabetes']

def extract_patient_id(filepath: Path) -> str:
    stem = filepath.stem
    match = re.search(r'\((\d+)\)', stem)
    if match:
        return f"{filepath.parent.name}_{match.group(1)}"
    return f"{filepath.parent.name}_unknown_{stem}"

records = []
for split in SPLITS:
    for cls in CLASSES:
        cls_dir = DATA_ROOT / split / cls
        if not cls_dir.exists():
            continue
        for img_path in sorted(cls_dir.iterdir()):
            if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                records.append({
                    'path': img_path,
                    'split': split,
                    'patient_id': extract_patient_id(img_path)
                })

df = pd.DataFrame(records)

train_pids = set(df[df['split'] == 'train']['patient_id'])
valid_pids = set(df[df['split'] == 'valid']['patient_id'])
test_pids = set(df[df['split'] == 'test']['patient_id'])

leak_tt = train_pids & test_pids
leak_tv = train_pids & valid_pids
leak_vt = valid_pids & test_pids

print(f"Train/Test Leakage: {leak_tt}")
print(f"Train/Valid Leakage: {leak_tv}")
print(f"Valid/Test Leakage: {leak_vt}")
