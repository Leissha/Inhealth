from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.actuators import router as actuators_router
from backend.app.api.device import router as device_router
from backend.app.api.readings import router as readings_router
from backend.app.api.settings import router as settings_router
from backend.app.api.summary import router as summary_router


app = FastAPI(
    title="Inhealth API",
    version="0.1.0",
    description="Edge-hosted API for the indoor air-quality monitor.",
)

# API Routers
app.include_router(readings_router)
app.include_router(settings_router)
app.include_router(actuators_router)
app.include_router(device_router)
app.include_router(summary_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


# Serve static production frontend when dist exists
DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if DIST_DIR.exists():
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(status_code=404, detail="API endpoint not found")

        file_path = (DIST_DIR / full_path).resolve()
        if not file_path.is_relative_to(DIST_DIR.resolve()):
            raise HTTPException(status_code=404, detail="File not found")
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))

        index_file = DIST_DIR / "index.html"
        if index_file.is_file():
            return FileResponse(str(index_file))

        raise HTTPException(status_code=404, detail="Frontend build not found")
