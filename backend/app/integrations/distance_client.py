import math
import logging
from typing import List, Dict, Any, Optional
from app.integrations.base_client import BaseClient
from app.core.config import settings

logger = logging.getLogger("travy.distance_client")

class DistanceClient(BaseClient):
    def __init__(self):
        provider = getattr(settings, "MAPS_PROVIDER", "local_haversine")
        self.provider = provider.lower() if provider else "local_haversine"
        
        # Google Maps base URL if configured, else Mapbox, else dummy
        base_url = "https://maps.googleapis.com"
        super().__init__(provider_name=self.provider, base_url=base_url)

    async def get_distance_matrix(self, origins: List[Dict[str, float]], destinations: List[Dict[str, float]], request_id: Optional[str] = None) -> Dict[str, Any]:
        # If explicitly local haversine, use fallback immediately
        if self.provider == "local_haversine" or not hasattr(settings, "GOOGLE_MAPS_API_KEY") or not getattr(settings, "GOOGLE_MAPS_API_KEY"):
            return self._calculate_haversine_matrix(origins, destinations)
            
        if self.provider == "google_maps":
            try:
                # Format coordinates: lat,lng separated by pipe '|'
                origins_str = "|".join([f"{o['lat']},{o['lng']}" for o in origins])
                destinations_str = "|".join([f"{d['lat']},{d['lng']}" for d in destinations])
                
                params = {
                    "origins": origins_str,
                    "destinations": destinations_str,
                    "key": getattr(settings, "GOOGLE_MAPS_API_KEY", "")
                }
                
                res = await self.request(
                    method="GET",
                    path="maps/api/distancematrix/json",
                    request_id=request_id,
                    params=params,
                    timeout=5.0
                )
                
                data = res["data"]
                if data.get("status") == "OK":
                    rows = []
                    for row in data.get("rows", []):
                        elements = []
                        for elem in row.get("elements", []):
                            if elem.get("status") == "OK":
                                duration_sec = elem["duration"]["value"]
                                distance_meters = elem["distance"]["value"]
                                elements.append({
                                    "status": "OK",
                                    "duration_value_seconds": duration_sec,
                                    "distance_value_meters": distance_meters
                                })
                            else:
                                elements.append({"status": "ZERO_RESULTS"})
                        rows.append({"elements": elements})
                        
                    return {
                        "provider": "google_maps",
                        "status": "ok",
                        "rows": rows
                    }
            except Exception as e:
                logger.warning(f"Google Maps Distance Matrix call failed: {e}. Falling back to Haversine.")
                
        return self._calculate_haversine_matrix(origins, destinations)

    def _calculate_haversine_matrix(self, origins: List[Dict[str, float]], destinations: List[Dict[str, float]]) -> Dict[str, Any]:
        rows = []
        for origin in origins:
            elements = []
            lat1, lon1 = origin["lat"], origin["lng"]
            for dest in destinations:
                lat2, lon2 = dest["lat"], dest["lng"]
                
                # Haversine distance
                R = 6371000 # Earth radius in meters
                phi1 = math.radians(lat1)
                phi2 = math.radians(lat2)
                dphi = math.radians(lat2 - lat1)
                dlambda = math.radians(dest["lng"] - origin["lng"])
                
                a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance_meters = int(R * c)
                
                # Assume average speed of 25 km/h (which is 6.94 m/s) in city traffic
                speed_mps = 25.0 / 3.6
                duration_seconds = int(distance_meters / speed_mps)
                
                elements.append({
                    "status": "OK",
                    "duration_value_seconds": duration_seconds,
                    "distance_value_meters": distance_meters
                })
            rows.append({"elements": elements})
            
        return {
            "provider": "local_haversine",
            "status": "fallback",
            "warning": "Maps distance API unavailable. Travel time is approximate.",
            "rows": rows
        }
