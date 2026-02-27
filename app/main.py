from fastapi import FastAPI

from app.api.routes.audit import router as audit_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router

app = FastAPI(title="Policy Mesh")
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(audit_router)
app.include_router(metrics_router)
