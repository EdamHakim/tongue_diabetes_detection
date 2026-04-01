from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    analysis_id: int
    created_at: datetime
    patient_id: str

    prediction: str
    risk_band: str
    probability_diabetes: float = Field(ge=0.0, le=1.0)
    confidence_pct: float = Field(ge=0.0, le=100.0)
    clinical_note: str

    original_image_url: str
    xai_overlay_url: str

    xai_legend: dict


class HistoryItem(BaseModel):
    analysis_id: int
    created_at: datetime
    prediction: str
    risk_band: str
    probability_diabetes: float

    original_image_url: str
    xai_overlay_url: str


class HistoryResponse(BaseModel):
    patient_id: str
    items: list[HistoryItem]

