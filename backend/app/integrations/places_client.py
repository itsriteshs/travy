import logging
import urllib.parse
from typing import List, Dict, Any, Optional
from app.integrations.base_client import BaseClient
from app.core.config import settings

logger = logging.getLogger("travy.places_client")

class PlacesClient(BaseClient):
    def __init__(self):
        provider = getattr(settings, "PLACES_PROVIDER", "overpass")
        self.provider = provider.lower() if provider else "overpass"
        
        base_url = "https://overpass-api.de/api"
        super().__init__(provider_name=self.provider, base_url=base_url)

    async def search_places(self, city_geo: dict, categories: List[str], limit: int = 15, request_id: Optional[str] = None) -> List[dict]:
        lat = city_geo.get("lat")
        lng = city_geo.get("lng")
        
        if self.provider == "overpass" and lat and lng:
            try:
                # Query Overpass API dynamically
                # around:6000 is 6km radius
                radius = 6000
                overpass_query = f"""[out:json][timeout:8];
(
  node["amenity"~"cafe|restaurant|food_court|marketplace"](around:{radius},{lat},{lng});
  node["tourism"~"attraction|viewpoint|museum|gallery|monument"](around:{radius},{lat},{lng});
  node["shop"~"mall|supermarket"](around:{radius},{lat},{lng});
  node["leisure"~"park|garden"](around:{radius},{lat},{lng});
);
out body {limit};"""
                
                res = await self.request(
                    method="POST",
                    path="interpreter",
                    request_id=request_id,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    json_data=None,
                    params={"data": overpass_query},
                    timeout=10.0
                )
                
                data = res["data"]
                elements = data.get("elements", [])
                
                candidates = []
                for elem in elements:
                    elem_id = str(elem.get("id", ""))
                    tags = elem.get("tags", {})
                    name = tags.get("name", tags.get("official_name", "Local Spot"))
                    
                    if name == "Local Spot":
                        continue
                        
                    category = "sightseeing"
                    if "amenity" in tags:
                        am = tags["amenity"]
                        if am in ["cafe", "restaurant", "food_court"]:
                            category = "food"
                        elif am in ["marketplace"]:
                            category = "market"
                    elif "shop" in tags:
                        category = "shopping"
                    elif "leisure" in tags:
                        category = "chill"
                    elif "tourism" in tags:
                        if tags["tourism"] in ["museum", "gallery"]:
                            category = "sightseeing"
                        else:
                            category = "photos"
                            
                    # Costs based on category
                    cost_map = {
                        "food": 250,
                        "market": 300,
                        "shopping": 400,
                        "sightseeing": 100,
                        "photos": 50,
                        "chill": 150
                    }
                    estimated_cost = cost_map.get(category, 100)
                    
                    addr = tags.get("addr:street", tags.get("addr:suburb", f"{city_geo.get('city')}, India"))
                    
                    candidates.append({
                        "id": f"op_{elem_id}",
                        "name": name,
                        "category": category,
                        "lat": elem.get("lat"),
                        "lng": elem.get("lon"),
                        "address": addr,
                        "source_provider": "overpass",
                        "rating": None, # OSM doesn't have ratings, set to None as per rules
                        "price_level": None,
                        "open_now": True,
                        "estimated_cost_inr": estimated_cost,
                        "confidence": 0.80
                    })
                
                if candidates:
                    return candidates[:limit]
            except Exception as e:
                logger.warning(f"Overpass search failed: {e}.")
                
        # If overpass failed, returned nothing, or is local_fallback, return empty list (no fabrication)
        return []
