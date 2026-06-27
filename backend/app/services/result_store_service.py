from typing import Dict, Any, Optional
from app.services.persistence_service import PersistenceService

class ResultStoreService:
    def save_result(self, result_id: str, request_id: str, result: dict, validation: dict, api_evidence: dict):
        PersistenceService.save_itinerary(result_id, request_id, result, validation, api_evidence)

    def get_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        return PersistenceService.get_itinerary(request_id)
