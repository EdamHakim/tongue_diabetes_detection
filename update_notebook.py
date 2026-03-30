import json

notebook_path = r'd:\Everything\ESPRIT\3IA\2eme semestre\AI Project\Act Phase\tongue_diabetes_detection\t2dm_tongue_detection.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

patches = {
    # Section 7: 3-Phase Training
    "## 7.": [
        "## 7. \ud83c\udfcb\ufe0f Ensemble Training — 3-Phase Strategy\n",
        "\n",
        "Each of the three backbones (**EfficientNet-B3**, **ConvNeXt-Tiny**, **ResNet-50**) is trained independently using `run_full_training()`, which applies the same 3-phase strategy:\n",
        "\n",
        "1. **Phase 1 — Head Warmup** (5 epochs): Only the classification head is trained; the backbone is fully frozen.\n",
        "2. **Phase 2 — Partial Unfreeze** (15 epochs): Architecture-specific tail blocks are unfrozen with a lower LR. Best checkpoint saved.\n",
        "3. **Phase 3 — Full Unfreeze** (10 epochs): All layers are unfrozen for final fine-tuning.\n",
        "\n",
        "> Each model's best weights are saved as `best_model_<backbone>.pth`.\n",
        "> After training, all three weights are loaded into `T2DMEnsemble` for soft-vote inference."
    ],

    # Section 10: Grad-CAM
    "## 10.": [
        "## 10. \ud83d\udd25 Ensemble Interpretability — Grad-CAM\n",
        "\n",
        "Grad-CAM highlights which tongue regions drive the **ensemble's** T2DM prediction. Since the ensemble averages probabilities from three backbones, we use the **EfficientNet-B3** sub-model (index 0) to generate saliency maps — it typically produces the most spatially meaningful activations for this task.\n",
        "\n",
        "> This is critical for clinical trust: activations should consistently fall on the tongue body, not the image background."
    ],

    # Section 10D: Patient Report
    "### 10D.": [
        "### 10D. \ud83d\udcc4 Ensemble Patient-Ready Explanation Report\n",
        "\n",
        "This function generates a clinical-grade report for a single image using the **full ensemble**. The prediction is confirmed across **three independent AI architectures** (EfficientNet-B3, ConvNeXt-Tiny, ResNet-50) via soft voting, making the result significantly more reliable than any single model would be."
    ],
}

fixed = []
for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        text = "".join(cell['source'])
        for trigger, new_source in patches.items():
            if text.startswith(trigger):
                cell['source'] = new_source
                fixed.append(trigger)
                break

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Fixed {len(fixed)} markdown cells: {fixed}")
