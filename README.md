# Glunova — Diabetic Tongue Detection (Full‑stack)

Patient-facing (and clinic-friendly) web app for **t2d_tongue_detection**:

- **Frontend**: React + Tailwind (clinical, accessible UI)
- **Backend**: FastAPI
- **Model/XAI**: loaded from `deploy_bundle/` (PyTorch ensemble + Grad‑CAM overlay)

## Run locally

### Backend (FastAPI)

From the repo root:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

Backend endpoints:

- `GET /health`
- `POST /api/analyze` (multipart: `patient_id`, `file`)
- `GET /api/history/{patient_id}`
- `GET /api/assets/{analysis_id}/{original|overlay}`

Stored data (SQLite + images) goes into `backend/data/` by default.

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Open the app at `http://localhost:5173`. The dev server proxies `/api` to `http://localhost:8000`.

## Core feature: `t2d_tongue_detection`

Flow:

1. Upload image + patient ID in the UI.
2. Frontend calls `POST /api/analyze`.
3. Backend runs:
   - **Prediction** via `deploy_bundle/inference_template.py` (`infer(path)`)
   - **XAI** via Grad‑CAM overlay (ensemble-averaged logit; EfficientNet target layer)
4. Backend returns prediction metadata + URLs for:
   - original image
   - XAI heatmap overlay image
5. Frontend shows:
   - side‑by‑side original vs overlay
   - risk badge + confidence
   - auto-generated clinical note
   - heatmap legend
   - optional history list per patient

## Modularity (swapping the bundle later)

All model/XAI integration is isolated behind a small adapter:

- `backend/app/services/model_adapter.py` (interface + helpers)
- `backend/app/services/deploy_bundle_adapter.py` (current implementation)

To replace the model or explanation method, implement a new adapter that satisfies:

- `predict(image_path) -> { probability_diabetes, prediction, risk_band }`
- `explain(image_path) -> overlay_png_bytes (+ legend metadata)`

Then swap the adapter used in `backend/app/main.py`.


