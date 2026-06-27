from typing import Dict, Any, Optional
from app.integrations.geocoder_client import GeocoderClient

class GeocodingService:
    def __init__(self):
        self.client = GeocoderClient()

    async def geocode_city(self, city: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.client.geocode_city(city, request_id)
