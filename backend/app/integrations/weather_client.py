import logging
from typing import Dict, Any, Optional
from app.integrations.base_client import BaseClient
from app.core.config import settings

logger = logging.getLogger("travy.weather_client")

class WeatherClient(BaseClient):
    def __init__(self):
        super().__init__(provider_name="weather", base_url="https://api.open-meteo.com/v1")

    async def get_weather(self, lat: float, lng: float, request_id: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": "weather_code,temperature_2m,relative_humidity_2m"
        }
        try:
            res = await self.request(
                method="GET",
                path="forecast",
                request_id=request_id,
                params=params,
                timeout=5.0
            )
            data = res.get("data", {})
            current = data.get("current", {})
            return {
                "temperature": current.get("temperature_2m", 25.0),
                "weather_code": current.get("weather_code", 0), # 0 is clear sky
                "humidity": current.get("relative_humidity_2m", 50.0),
                "provider": "open_meteo",
                "status": "success"
            }
        except Exception as e:
            logger.warning(f"Failed to fetch weather from Open-Meteo: {e}")
            return {
                "temperature": 25.0,
                "weather_code": 0,
                "humidity": 50.0,
                "provider": "open_meteo",
                "status": "error",
                "error": str(e)
            }
