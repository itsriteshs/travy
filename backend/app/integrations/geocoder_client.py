import logging
from typing import Dict, Any, Optional
from app.integrations.base_client import BaseClient
from app.core.config import settings

logger = logging.getLogger("travy.geocoder_client")

class GeocoderClient(BaseClient):
    def __init__(self):
        provider = getattr(settings, "GEOCODER_PROVIDER", "nominatim")
        self.provider = provider.lower() if provider else "nominatim"
        
        base_url = "https://nominatim.openstreetmap.org"
        super().__init__(provider_name=self.provider, base_url=base_url)

    async def geocode_city(self, city: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        if self.provider == "nominatim":
            try:
                headers = {"User-Agent": "Travy/0.1.0 (contact@travy.ai)"}
                params = {
                    "q": city,
                    "format": "json",
                    "limit": 1
                }
                
                # Fetch geocoding through BaseClient to log the call
                res = await self.request(
                    method="GET",
                    path="search",
                    request_id=request_id,
                    headers=headers,
                    params=params,
                    timeout=5.0
                )
                
                data = res["data"]
                if data and isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    bbox = [float(x) for x in item.get("boundingbox", [0,0,0,0])]
                    return {
                        "city": city,
                        "lat": float(item["lat"]),
                        "lng": float(item["lon"]),
                        "bbox": bbox,
                        "provider": "nominatim",
                        "confidence": 0.95
                    }
            except Exception as e:
                logger.warning(f"Nominatim geocoding failed for {city}: {e}.")
                
        raise ValueError(f"Unable to geocode city '{city}' using real-time service.")
