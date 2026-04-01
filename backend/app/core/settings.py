from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Glunova API"
    cors_origins: list[str] = ["http://localhost:5173"]
    storage_dir: str = "backend/data"
    bundle_dir: str = "deploy_bundle"


settings = Settings()

