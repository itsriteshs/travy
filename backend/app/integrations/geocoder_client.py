import logging
from typing import Dict, Any, Optional
from app.integrations.base_client import BaseClient
from app.core.config import settings

logger = logging.getLogger("travy.geocoder_client")

# Predefined coordinates for common cities as a robust fallback
CITY_FALLBACKS = {
    "delhi": {"city": "Delhi", "lat": 28.6139, "lng": 77.2090, "bbox": [28.4, 28.9, 76.8, 77.4], "provider": "local_fallback", "confidence": 0.90},
    "bangalore": {"city": "Bangalore", "lat": 12.9716, "lng": 77.5946, "bbox": [12.8, 13.1, 77.4, 77.8], "provider": "local_fallback", "confidence": 0.90},
    "bengaluru": {"city": "Bangalore", "lat": 12.9716, "lng": 77.5946, "bbox": [12.8, 13.1, 77.4, 77.8], "provider": "local_fallback", "confidence": 0.90},
    "jaipur": {"city": "Jaipur", "lat": 26.9124, "lng": 75.7873, "bbox": [26.8, 27.0, 75.6, 75.9], "provider": "local_fallback", "confidence": 0.90},
    "goa": {"city": "Goa", "lat": 15.2993, "lng": 74.1240, "bbox": [14.8, 15.8, 73.6, 74.4], "provider": "local_fallback", "confidence": 0.90},
    "pune": {"city": "Pune", "lat": 18.5204, "lng": 73.8567, "bbox": [18.4, 18.6, 73.7, 74.0], "provider": "local_fallback", "confidence": 0.90},
    "mumbai": {"city": "Mumbai", "lat": 19.0760, "lng": 72.8777, "bbox": [18.8, 19.3, 72.7, 73.0], "provider": "local_fallback", "confidence": 0.90},
}

class GeocoderClient(BaseClient):
    def __init__(self):
        provider = getattr(settings, "GEOCODER_PROVIDER", "nominatim")
        self.provider = provider.lower() if provider else "nominatim"
        
        base_url = "https://nominatim.openstreetmap.org"
        super().__init__(provider_name=self.provider, base_url=base_url)

    async def geocode_city(self, city: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        city_key = city.lower().strip()
        
        # If provider is configured as local fallback, use that immediately
        if self.provider == "local_fallback" and city_key in CITY_FALLBACKS:
            return CITY_FALLBACKS[city_key]
            
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
                    # Parse boundingbox which is [latmin, latmax, lonmin, lonmax]
                    bbox = [float(x) for x in item.get("boundingbox", [0,0,0,0])]
                    # Reorder to [latmin, latmax, lonmin, lonmax] or match schema
                    return {
                        "city": city,
                        "lat": float(item["lat"]),
                        "lng": float(item["lon"]),
                        "bbox": bbox,
                        "provider": "nominatim",
                        "confidence": 0.95
                    }
            except Exception as e:
                logger.warning(f"Nominatim geocoding failed for {city}: {e}. Falling back to local data.")
                
        # If we failed or if city is recognized in fallbacks
        if city_key in CITY_FALLBACKS:
            return CITY_FALLBACKS[city_key]
            
        # Generic default coordinate fallback if completely unknown city
        return {
            "city": city,
            "lat": 28.6139,
            "lng": 77.2090,
            "bbox": [28.4, 28.9, 76.8, 77.4],
            "provider": "generic_fallback",
            "confidence": 0.50
        }
