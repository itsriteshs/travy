from typing import List, Dict, Any
from app.services.persistence_service import PersistenceService

class ApiCallLoggerService:
    def get_logs_for_request(self, request_id: str) -> List[Dict[str, Any]]:
        return PersistenceService.get_api_calls(request_id)
