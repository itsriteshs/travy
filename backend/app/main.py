from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.ai_smoke import router as ai_smoke_router
from app.api.security import router as security_router
from app.api.planner import router as planner_router
from app.api.integrations import router as integrations_router
from app.api.demo import router as demo_router
from app.services.persistence_service import PersistenceService

app = FastAPI(
    title="Travy Backend",
    description="FastAPI Backend for Travy",
    version="0.1.0"
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    PersistenceService.init_db()

# Register routers
app.include_router(health_router)
app.include_router(ai_smoke_router)
app.include_router(security_router)
app.include_router(planner_router)
app.include_router(integrations_router)
app.include_router(demo_router)
