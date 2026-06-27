from fastapi import APIRouter
from app.services.integration_health_service import IntegrationHealthService
from app.services.otari_usage_service import OtariUsageService
from app.services.otari_client import OtariClient
from app.core.config import settings

router = APIRouter()

@router.get("/api/integrations/health")
async def get_health():
    service = IntegrationHealthService()
    return await service.check_health()

@router.get("/api/integrations/otari")
async def check_otari():
    client = OtariClient()
    try:
        res = await client.generate_completion(
            model=settings.OTARI_CHEAP_MODEL,
            prompt="ping",
            max_tokens=1
        )
        return {"status": "healthy", "details": res}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/api/router/live-usage")
def get_live_usage():
    service = OtariUsageService()
    return service.get_router_usage("demo")
