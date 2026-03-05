from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.audit import router as audit_router
from app.core.policy_file import PolicyFileError
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.routes import router as routes_router

app = FastAPI(title="Policy Mesh")


@app.exception_handler(PolicyFileError)
def policy_file_error_handler(request, exc: PolicyFileError):
    """Return 500 when POLICY_FILE is unset or file is missing/invalid."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(audit_router)
app.include_router(metrics_router)
app.include_router(routes_router)

# Minimal UI (T-203): static page at / and /ui; mount after API routers so /v1/* is not shadowed.
_STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/")
def serve_ui_root():
    """Serve the minimal UI at the app root."""
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/ui")
def serve_ui_path():
    """Serve the minimal UI at /ui."""
    return FileResponse(_STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
