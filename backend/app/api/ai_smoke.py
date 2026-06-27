from fastapi import APIRouter
from app.core.config import settings
from app.services.otari_client import OtariClient

router = APIRouter(prefix="/api/ai")

@router.get("/smoke")
async def run_smoke_test():
    client = OtariClient()
    try:
        result = await client.generate_completion(
            model=settings.OTARI_CHEAP_MODEL,
            prompt="Reply with exactly: travy-ok",
            max_tokens=5
        )
        return result
    except Exception as e:
        return {
            "backend": True,
            "otari_reachable": False,
            "mode": "otari_unavailable",
            "error_type": type(e).__name__,
            "safe_fallback_available": True
        }

@router.get("/models")
def get_models():
    return {
        "local": settings.OTARI_LOCAL_LLM_MODEL,
        "cheap": settings.OTARI_CHEAP_MODEL,
        "balanced": settings.OTARI_BALANCED_MODEL,
        "strong": settings.OTARI_STRONG_MODEL
    }
