from __future__ import annotations

import base64
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypedDict

import numpy as np
from PIL import Image


class InferenceResult(TypedDict):
    probability_diabetes: float
    prediction: str
    risk_band: str


@dataclass(frozen=True)
class XaiResult:
    overlay_png_bytes: bytes
    cam_colormap: str
    cam_alpha: float


class ModelAdapter(Protocol):
    def predict(self, image_path: str) -> InferenceResult: ...

    def explain(self, image_path: str) -> XaiResult: ...


def b64_png(png_bytes: bytes) -> str:
    return base64.b64encode(png_bytes).decode("ascii")


def save_png_bytes(path: Path, png_bytes: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_bytes)


def pil_save_normalized_rgb_png(src_path: str, dst_path: Path, size: int | None = None) -> None:
    img = Image.open(src_path).convert("RGB")
    if size is not None:
        img = img.resize((size, size))
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst_path, format="PNG")


def atomic_temp_path(suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path

