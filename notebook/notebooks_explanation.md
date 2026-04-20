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

---

## 2. Model Training & Evaluation (`tongue_t2d_training.ipynb`)

This notebook handles the architecture selection, training logic, and performance analysis.

### Key Components:
*   **Preprocessing Pipeline**:
    *   **MediaPipe Integration**: Uses Google's MediaPipe Face Mesh to detect inner lip landmarks and crop the tongue area accurately.
    *   **Circular Masking**: Applies a radial gradient mask to center the model's attention on the tongue texture and ignore background artifacts.
*   **Model Architectures**: Trains and compares three backbones:
    1.  **EfficientNet-B2**: Efficient balance of parameters and accuracy.
    2.  **ResNet-50**: A deep residual network used as a baseline.
    3.  **MobileNet-V3-Large**: Optimized for potential deployment on mobile devices.
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
