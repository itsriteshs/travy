from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def get_health():
    return {"status": "ok", "backend": True}

@router.get("/ready")
def get_ready():
    return {"status": "ready", "backend": True}
