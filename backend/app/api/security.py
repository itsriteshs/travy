from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.injection_service import InjectionService

router = APIRouter(prefix="/api/security")

class ScanRequest(BaseModel):
    text: Optional[str] = None
    prompt: Optional[str] = None

@router.post("/scan")
def scan_text(request: ScanRequest):
    input_text = request.text or request.prompt or ""
    service = InjectionService()
    return service.scan(input_text)
