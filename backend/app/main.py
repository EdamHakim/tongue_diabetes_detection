from __future__ import annotations

import mimetypes
import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .core.db import Base, SessionLocal, engine
from .core.settings import settings
from .models import Analysis
from .schemas import AnalyzeResponse, HistoryItem, HistoryResponse
from .services.clinical_note import confidence_pct, make_clinical_note
from .services.deploy_bundle_adapter import DeployBundleAdapter
from .services.model_adapter import pil_save_normalized_rgb_png, save_png_bytes


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _storage_root() -> Path:
    root = Path(settings.storage_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _assets_dir() -> Path:
    d = _storage_root() / "assets"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_patient_id(patient_id: str) -> str:
    pid = patient_id.strip()
    if not pid:
        raise HTTPException(status_code=400, detail="patient_id is required")
    if any(c in pid for c in ["/", "\\", ":", "\0"]):
        raise HTTPException(status_code=400, detail="patient_id contains invalid characters")
    return pid


def _validate_upload(file: UploadFile) -> None:
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="No file provided")
    ct = (file.content_type or "").lower()
    if ct not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ct or 'unknown'}")


app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"ok": True, "name": settings.app_name}


@app.get("/api/assets/{analysis_id}/{kind}")
def get_asset(analysis_id: int, kind: str, db: Session = Depends(get_db)):
    if kind not in {"original", "overlay"}:
        raise HTTPException(status_code=404, detail="Asset not found")
    a = db.get(Analysis, analysis_id)
    if a is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    p = Path(a.original_path if kind == "original" else a.overlay_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Asset missing on server")
    media_type, _ = mimetypes.guess_type(p.name)
    return FileResponse(str(p), media_type=media_type or "image/png")


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(
    patient_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    patient_id = _safe_patient_id(patient_id)
    _validate_upload(file)

    # Save upload to disk first (keeps model adapter simple).
    assets = _assets_dir()
    tmp_dir = _storage_root() / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"upload_{datetime.utcnow().timestamp()}_{os.getpid()}"
    with tmp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        adapter = DeployBundleAdapter(bundle_dir=Path(settings.bundle_dir))
        pred = adapter.predict(str(tmp_path))
        xai = adapter.explain(str(tmp_path))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model failure: {type(e).__name__}: {e}")

    prob = float(pred["probability_diabetes"])
    a = Analysis(
        patient_id=patient_id,
        prediction=str(pred["prediction"]),
        risk_band=str(pred["risk_band"]),
        probability_diabetes=prob,
        original_path="",  # filled after save
        overlay_path="",
    )
    db.add(a)
    db.commit()
    db.refresh(a)

    original_path = assets / f"{a.id}_original.png"
    overlay_path = assets / f"{a.id}_overlay.png"

    # Save a normalized PNG for consistent frontend rendering.
    pil_save_normalized_rgb_png(str(tmp_path), original_path, size=None)
    save_png_bytes(overlay_path, xai.overlay_png_bytes)

    a.original_path = str(original_path)
    a.overlay_path = str(overlay_path)
    db.commit()
    try:
        tmp_path.unlink(missing_ok=True)  # type: ignore[arg-type]
    except Exception:
        pass

    return AnalyzeResponse(
        analysis_id=a.id,
        created_at=a.created_at,
        patient_id=a.patient_id,
        prediction=a.prediction,
        risk_band=a.risk_band,
        probability_diabetes=a.probability_diabetes,
        confidence_pct=confidence_pct(a.probability_diabetes),
        clinical_note=make_clinical_note(risk_band=a.risk_band, probability_diabetes=a.probability_diabetes),
        original_image_url=f"/api/assets/{a.id}/original",
        xai_overlay_url=f"/api/assets/{a.id}/overlay",
        xai_legend={
            "type": "heatmap_overlay",
            "meaning": "Warmer colors indicate regions that most increased the model's diabetes score.",
            "low_label": "Lower influence",
            "high_label": "Higher influence",
            "colormap": xai.cam_colormap,
            "alpha": xai.cam_alpha,
        },
    )


@app.get("/api/history/{patient_id}", response_model=HistoryResponse)
def history(patient_id: str, db: Session = Depends(get_db)):
    patient_id = _safe_patient_id(patient_id)
    q = (
        select(Analysis)
        .where(Analysis.patient_id == patient_id)
        .order_by(Analysis.created_at.desc(), Analysis.id.desc())
        .limit(50)
    )
    rows = db.execute(q).scalars().all()
    return HistoryResponse(
        patient_id=patient_id,
        items=[
            HistoryItem(
                analysis_id=a.id,
                created_at=a.created_at,
                prediction=a.prediction,
                risk_band=a.risk_band,
                probability_diabetes=a.probability_diabetes,
                original_image_url=f"/api/assets/{a.id}/original",
                xai_overlay_url=f"/api/assets/{a.id}/overlay",
            )
            for a in rows
        ],
    )

