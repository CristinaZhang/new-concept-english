from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import HealthResponse, settings
from app.db.database import init_db
from app.routers import lessons, vocabulary, grammar, progress


def create_app() -> FastAPI:
    app = FastAPI(
        title="New Concept English API",
        version="0.1.0",
    )

    # CORS
    origins = [o.strip() for o in (settings.cors_origins or "").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # API routes
    app.include_router(lessons.router, prefix="/v1")
    app.include_router(vocabulary.router, prefix="/v1")
    app.include_router(grammar.router, prefix="/v1")
    app.include_router(progress.router, prefix="/v1")

    # Static resources — mount the project-level resources/ dir
    resources_dir = Path(__file__).resolve().parents[2] / "resources"
    if resources_dir.exists():
        app.mount("/resources", StaticFiles(directory=str(resources_dir)), name="resources")

    return app


app = create_app()


@app.on_event("startup")
def _startup() -> None:
    # Ensure data directory exists
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        if not db_path.startswith(":memory:"):
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    init_db()
