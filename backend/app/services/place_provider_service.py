from typing import List, Dict, Any, Optional
from app.integrations.places_client import PlacesClient

class PlaceProviderService:
    def __init__(self):
        self.client = PlacesClient()

    async def search_places(self, city_geo: dict, categories: List[str], limit: int = 15, request_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self.client.search_places(city_geo, categories, limit, request_id)
