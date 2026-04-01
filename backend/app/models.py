from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .core.db import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    patient_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    prediction: Mapped[str] = mapped_column(String, nullable=False)
    risk_band: Mapped[str] = mapped_column(String, nullable=False)
    probability_diabetes: Mapped[float] = mapped_column(Float, nullable=False)

    original_path: Mapped[str] = mapped_column(String, nullable=False)
    overlay_path: Mapped[str] = mapped_column(String, nullable=False)

