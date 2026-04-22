import json
import os

notebook_path = r'd:\Everything\ESPRIT\3IA\2eme semestre\AI Project\Act Phase\tongue_diabetes_detection\notebook\tongue_t2d_training.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def create_markdown(content_list):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [c + "\n" for c in content_list]
    }

# 1. Model Justification (Before Section 3)
model_justification = create_markdown([
    "### Model choices justified by your data",
    "",
    "**Your dataset has ~250 unique images per class** after excluding augments. That is a very small medical dataset. Every choice below is driven by that constraint.",
    "",
    "*   **EfficientNet-B2 (primary)**. At 9.2M parameters it is the most sample-efficient model family for medical image classification. Its compound scaling (depth + width + resolution together) means it extracts rich color and texture features — exactly what tongue diagnosis relies on — without overfitting on 250 images per class.",
    "*   **ResNet-50 (baseline/ablation)**. Chosen as the 'sweet spot' in the ResNet family. While ResNet-18/34 are too shallow for subtle texture features, and ResNet-101/152 overfit on small medical datasets, ResNet-50 provides the optimal depth. It is also the industry standard for TCM research.",
    "*   **MobileNetV3-Large (Kaggle efficiency)**. Kaggle P100/T4 GPUs have limited VRAM. With only 4.2M parameters and depthwise separable convolutions, it allows for larger batch sizes and potential mobile deployment.",
    "",
    "**Why not ViT or Swin?** Your dataset is too small. Vision Transformers need 10k+ images to outperform CNNs via transfer learning; with only 700 training samples, attention heads overfit to augmentation artifacts.",
    "",
    "**Data Leakage Prevention**: Augmented images share a source identity. Any naive random split will leak source images into validation, giving inflated metrics. The pipeline uses a group-aware split to get honest numbers."
])

# 2. Training Strategy (Before Section 4)
training_strategy = create_markdown([
    "### Advanced Training Strategy",
    "",
    "1.  **Focal Loss**: Standard CrossEntropy can be dominated by 'easy' examples. We use Focal Loss ($\gamma=2.0$) to force the model to focus on 'hard' examples—those with subtle diabetic textures.",
    "2.  **Two-Stage Transfer Learning**:",
    "    *   **Warmup**: The backbone is frozen, and only the new classifier head is trained.",
    "    *   **Fine-tuning**: The last few layers of the backbone are unfrozen with a much lower learning rate to adapt features to specific tongue characteristics.",
    "3.  **Mixup Augmentation**: We blend pairs of images and labels during training. This regularizes the model and improves generalization to noisy real-world images."
])

# 3. Clinical Logic (Before Section 6)
clinical_logic = create_markdown([
    "### Clinical Evaluation Logic",
    "",
    "*   **Precision-Targeted Thresholding**: In medical diagnostics, a False Positive is costly. We tune the classification threshold to maintain a **minimum 90% Precision** on the validation set.",
    "*   **Explainability (Grad-CAM)**: We generate heatmaps to show which tongue regions (cracks, coating color, etc.) influenced the model, ensuring it isn't making decisions based on background noise."
])

# Insert logic
insertions = [
    ("## 3. Model Definitions", model_justification),
    ("## 4. Training Loop", training_strategy),
    ("## 6. Model Selection", clinical_logic)
]

for title, cell in insertions:
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'markdown' and title in ''.join(c['source']):
            nb['cells'].insert(i, cell)
            break

# Save back
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print("Successfully updated notebook with multiple technical justifications.")
