from __future__ import annotations

import contextlib
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from PIL import Image

from .model_adapter import InferenceResult, ModelAdapter, XaiResult


@contextlib.contextmanager
def _chdir(path: Path):
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


class _EnsembleCamModel(nn.Module):
    def __init__(self, models: list[nn.Module]):
        super().__init__()
        self.models = nn.ModuleList(models)

    def forward(self, x):  # (B,3,H,W)
        logits = [m(x) for m in self.models]  # each (B,)
        z = torch.stack(logits, dim=0).mean(dim=0)  # (B,)
        return torch.stack([-z, z], dim=1)  # (B,2)


@dataclass
class DeployBundleAdapter(ModelAdapter):
    """
    Adapter for the provided `deploy_bundle/` format.

    Notes:
    - The bundle's `inference_template.py` uses relative paths (artifacts/...), so we import/run it
      while temporarily chdir'd into the bundle directory.
    - XAI uses Grad-CAM on the ensemble-averaged logit, targeting EfficientNet-B3's conv head.
    """

    bundle_dir: Path
    _bundle: Any | None = None
    _cam: Any | None = None
    _cam_model: nn.Module | None = None
    _target_layers: list[Any] | None = None

    def _ensure_loaded(self) -> None:
        if self._bundle is not None:
            return

        self.bundle_dir = self.bundle_dir.resolve()
        if not self.bundle_dir.exists():
            raise FileNotFoundError(f"deploy_bundle not found at: {self.bundle_dir}")

        # Make bundle importable (for inference_template.py)
        if str(self.bundle_dir) not in sys.path:
            sys.path.insert(0, str(self.bundle_dir))

        with _chdir(self.bundle_dir):
            self._bundle = importlib.import_module("inference_template")

        # Prepare CAM pieces lazily; only if Grad-CAM is installed/available.
        try:
            from pytorch_grad_cam import GradCAM
        except Exception:
            self._cam = None
            return

        models: list[nn.Module] = list(self._bundle.MODELS)  # type: ignore[attr-defined]
        for m in models:
            m.eval()

        self._cam_model = _EnsembleCamModel(models)

        # Mirror notebook choice: use EfficientNet-B3 backbone conv_head.
        effnet = models[0]
        if not hasattr(effnet, "backbone") or not hasattr(effnet.backbone, "conv_head"):
            raise RuntimeError(
                "Grad-CAM target layer not found. Expected EfficientNet model at index 0 with `backbone.conv_head`."
            )

        self._target_layers = [effnet.backbone.conv_head]
        self._cam = GradCAM(model=self._cam_model, target_layers=self._target_layers)

    def predict(self, image_path: str) -> InferenceResult:
        self._ensure_loaded()
        assert self._bundle is not None

        with _chdir(self.bundle_dir):
            out = self._bundle.infer(image_path)  # type: ignore[attr-defined]
        return out

    def explain(self, image_path: str) -> XaiResult:
        self._ensure_loaded()
        if self._cam is None or self._bundle is None:
            raise RuntimeError(
                "XAI pipeline is not available. Install `pytorch-grad-cam` in the backend environment."
            )

        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        from pytorch_grad_cam.utils.image import show_cam_on_image

        img_size = int(self._bundle.IMG_SIZE)  # type: ignore[attr-defined]

        # Use the bundle's preprocessing to ensure identical normalization.
        with _chdir(self.bundle_dir):
            x = self._bundle.preprocess_rgb(image_path)  # type: ignore[attr-defined]

        # Grad-CAM for diabetes class (index 1)
        grayscale_cam = self._cam(input_tensor=x, targets=[ClassifierOutputTarget(1)])[0]

        pil = Image.open(image_path).convert("RGB").resize((img_size, img_size))
        rgb = np.asarray(pil).astype(np.float32) / 255.0
        overlay = show_cam_on_image(rgb, grayscale_cam, use_rgb=True)

        out_pil = Image.fromarray(overlay)
        import io

        b = io.BytesIO()
        out_pil.save(b, format="PNG")

        return XaiResult(overlay_png_bytes=b.getvalue(), cam_colormap="jet", cam_alpha=0.5)

