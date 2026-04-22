# Tongue Diabetes Detection: Notebooks Explanation

This project implements a machine learning pipeline to detect Type 2 Diabetes (T2D) using tongue images. It is divided into two main stages: Data Preparation and Model Training.

---

## 1. Data Preparation & Augmentation (`tongue-dataprep.ipynb`)

The primary goal of this notebook is to transform raw, unbalanced data into a standardized, balanced, and leakage-proof dataset suitable for deep learning.

### Key Features:
*   **Leakage Prevention**: It uses a "canonical key" grouping strategy. If multiple images are variations of the same original (flips, rotations), it ensures they all stay within the same split (Train/Val/Test). This prevents the model from "cheating" by seeing a variation of a test image during training.
*   **Offline Augmentation**: Uses the `albumentations` library to perform horizontal flips, shifts, scales, rotations, and brightness/contrast adjustments.
*   **Automated Balancing**: It calculates the distribution of classes and performs controlled oversampling for the minority class (diabetes) until the dataset is balanced across all splits.
*   **Verification**: Includes MD5 hash collision checks to prove that no identical images exist across different splits.
*   **Output**: Generates a structured directory (`train/`, `val/`, `test/`) and bundles them into ZIP files for easy distribution.

### The Importance of `family_id`
All augmented versions of an original image share the same source identity (referred to as a `family_id` or canonical group). A naive random split would leak these variations across training and validation, leading to "over-optimistic" (inflated) metrics. The pipeline performs a **stratified group split**, ensuring that all variations of a single tongue image stay together in the same split for honest evaluation.


---

## 2. Model Training & Evaluation (`tongue_t2d_training.ipynb`)

This notebook handles the architecture selection, training logic, and performance analysis.

### Key Components:
*   **Preprocessing Pipeline**:
    *   **MediaPipe Integration**: Uses Google's MediaPipe Face Mesh to detect inner lip landmarks and crop the tongue area accurately.
    *   **Circular Masking**: Applies a radial gradient mask to center the model's attention on the tongue texture and ignore background artifacts.
*   **Model Architectures**:
    We compared three backbones, selected specifically for their performance on small medical datasets:
    1.  **EfficientNet-B2 (Primary)**: At 9.2M parameters, it's highly sample-efficient. Its compound scaling (depth+width+resolution) extracts the rich color and texture features critical for tongue diagnosis without overfitting on small samples.
    2.  **ResNet-50 (Baseline)**: Chosen as the "sweet spot" in the ResNet family. While ResNet-18/34 are too shallow for subtle texture features, and ResNet-101/152 overfit on small medical datasets, ResNet-50 provides the optimal depth. Its use of "bottleneck" blocks (1x1 convolutions) allows for sophisticated feature extraction with a manageable parameter count. It is also the most common benchmark in Traditional Chinese Medicine (TCM) imaging literature.
    3.  **MobileNet-V3-Large**: Selected for its low parameter count (4.2M) and depthwise separable convolutions, allowing for larger batch sizes on Kaggle GPUs and suitability for mobile deployment.

### Advanced Training Strategy
1.  **Focal Loss**: Standard CrossEntropy can be dominated by "easy" examples. We use Focal Loss with $\gamma=2.0$ to force the model to focus on "hard" examples—those with subtle diabetic textures that are difficult to distinguish.
2.  **Two-Stage Transfer Learning**:
    *   **Warmup**: The backbone is frozen, and only the new classifier head is trained.
    *   **Fine-tuning**: The last few layers of the backbone are unfrozen with a much lower learning rate ($10^{-4}$) to adapt the pre-trained features to specific tongue characteristics.
3.  **Mixup Augmentation**: We blend pairs of images and their labels during training. This regularizes the model and prevents it from becoming "too confident" in its predictions, improving its ability to handle noisy real-world images.

### Why CNNs instead of Transformers?
Given the dataset size (~250 unique images per class), Vision Transformers (ViT/Swin) were avoided. Transformers typically require 10k+ images to outperform CNNs via transfer learning; with only 700 training samples, attention heads are prone to overfitting on augmentation artifacts.

*   **Training Strategy**:
    *   **Focal Loss**: Used to penalize the model more heavily for misclassifying "hard" examples.
    *   **Mixup Augmentation**: Blends images and labels to improve generalization.
    *   **Two-Stage Training**: A "warmup" phase for the classifier followed by a "fine-tuning" phase where late backbone layers are unfrozen.
*   **Evaluation & Explainability**:
    *   **Threshold Tuning**: Optimizes the probability threshold to reach a specific **Precision target (e.g., >90%)**, ensuring the model is reliable for clinical scenarios.
    *   **Grad-CAM Visualization**: Produces heatmaps highlighting the regions of the tongue (e.g., coating, color, or edge cracks) that influenced the model's prediction.

---

## Technical Stack
| Category | Tools/Libraries |
| :--- | :--- |
| **Framework** | PyTorch |
| **Augmentation** | Albumentations, Torchvision |
| **Vision Tools** | MediaPipe, OpenCV |
| **Metrics** | Scikit-learn (ROC-AUC, PR-AUC, F1) |
| **Explainability** | Pytorch-Grad-CAM |
