import logging
import urllib.parse
from typing import List, Dict, Any, Optional
from app.integrations.base_client import BaseClient
from app.core.config import settings

logger = logging.getLogger("travy.places_client")

# Seeded local candidates for major cities as immediate fallbacks
LOCAL_SEEDS = {
    "delhi": [
        {"id": "dl_janpath", "name": "Janpath Market", "category": "market", "lat": 28.6271, "lng": 77.2195, "address": "Janpath, New Delhi", "source_provider": "local_fallback", "rating": 4.3, "price_level": 1, "open_now": True, "estimated_cost_inr": 300, "confidence": 0.85},
        {"id": "dl_khan_mkt", "name": "Khan Market", "category": "market", "lat": 28.6002, "lng": 77.2273, "address": "Rabindra Nagar, New Delhi", "source_provider": "local_fallback", "rating": 4.5, "price_level": 3, "open_now": True, "estimated_cost_inr": 600, "confidence": 0.90},
        {"id": "dl_india_gate", "name": "India Gate", "category": "monument", "lat": 28.6129, "lng": 77.2295, "address": "Kartavya Path, New Delhi", "source_provider": "local_fallback", "rating": 4.7, "price_level": 0, "open_now": True, "estimated_cost_inr": 20, "confidence": 0.95},
        {"id": "dl_cp", "name": "Connaught Place", "category": "shopping street", "lat": 28.6304, "lng": 77.2177, "address": "Connaught Place, New Delhi", "source_provider": "local_fallback", "rating": 4.4, "price_level": 2, "open_now": True, "estimated_cost_inr": 400, "confidence": 0.88},
        {"id": "dl_saravana", "name": "Saravana Bhavan", "category": "restaurant", "lat": 28.6315, "lng": 77.2197, "address": "Janpath, Connaught Place, New Delhi", "source_provider": "local_fallback", "rating": 4.3, "price_level": 1, "open_now": True, "estimated_cost_inr": 250, "confidence": 0.85},
        {"id": "dl_lodhi", "name": "Lodhi Garden", "category": "garden", "lat": 28.5931, "lng": 77.2198, "address": "Lodhi Road, New Delhi", "source_provider": "local_fallback", "rating": 4.6, "price_level": 0, "open_now": True, "estimated_cost_inr": 0, "confidence": 0.92},
        {"id": "dl_kunzum", "name": "Kunzum Travel Cafe", "category": "cafe", "lat": 28.5301, "lng": 77.2012, "address": "Hauz Khas Village, New Delhi", "source_provider": "local_fallback", "rating": 4.2, "price_level": 1, "open_now": True, "estimated_cost_inr": 200, "confidence": 0.80},
        {"id": "dl_national_museum", "name": "National Museum", "category": "museum", "lat": 28.6118, "lng": 77.2192, "address": "Janpath, New Delhi", "source_provider": "local_fallback", "rating": 4.5, "price_level": 1, "open_now": True, "estimated_cost_inr": 150, "confidence": 0.88}
    ],
    "bangalore": [
        {"id": "blr_cubbon", "name": "Cubbon Park", "category": "garden", "lat": 12.9779, "lng": 77.5952, "address": "Kasturba Road, Bengaluru", "source_provider": "local_fallback", "rating": 4.6, "price_level": 0, "open_now": True, "estimated_cost_inr": 0, "confidence": 0.95},
        {"id": "blr_toit", "name": "Toit Brewpub", "category": "restaurant", "lat": 12.9791, "lng": 77.6407, "address": "Indiranagar, Bengaluru", "source_provider": "local_fallback", "rating": 4.5, "price_level": 3, "open_now": True, "estimated_cost_inr": 800, "confidence": 0.90},
        {"id": "blr_mg_road", "name": "MG Road Shopping Street", "category": "shopping street", "lat": 12.9743, "lng": 77.6083, "address": "MG Road, Bengaluru", "source_provider": "local_fallback", "rating": 4.2, "price_level": 2, "open_now": True, "estimated_cost_inr": 300, "confidence": 0.85},
        {"id": "blr_commercial", "name": "Commercial Street", "category": "market", "lat": 12.9822, "lng": 77.6086, "address": "Tasker Town, Bengaluru", "source_provider": "local_fallback", "rating": 4.1, "price_level": 1, "open_now": True, "estimated_cost_inr": 250, "confidence": 0.82},
        {"id": "blr_palace", "name": "Bangalore Palace", "category": "monument", "lat": 12.9980, "lng": 77.5920, "address": "Vasanth Nagar, Bengaluru", "source_provider": "local_fallback", "rating": 4.4, "price_level": 2, "open_now": True, "estimated_cost_inr": 250, "confidence": 0.88},
        {"id": "blr_lalbagh", "name": "Lalbagh Botanical Garden", "category": "garden", "lat": 12.9507, "lng": 77.5900, "address": "Mavalli, Bengaluru", "source_provider": "local_fallback", "rating": 4.5, "price_level": 1, "open_now": True, "estimated_cost_inr": 50, "confidence": 0.90},
        {"id": "blr_corner_house", "name": "Corner House Ice Cream", "category": "cafe", "lat": 12.9602, "lng": 77.6012, "address": "Lavelle Road, Bengaluru", "source_provider": "local_fallback", "rating": 4.7, "price_level": 1, "open_now": True, "estimated_cost_inr": 180, "confidence": 0.88},
        {"id": "blr_blossom", "name": "Blossom Book House", "category": "bookstore", "lat": 12.9752, "lng": 77.6065, "address": "Church Street, Bengaluru", "source_provider": "local_fallback", "rating": 4.6, "price_level": 1, "open_now": True, "estimated_cost_inr": 100, "confidence": 0.85}
    ],
    "jaipur": [
        {"id": "jp_hawa_mahal", "name": "Hawa Mahal", "category": "monument", "lat": 26.9239, "lng": 75.8267, "address": "Badi Choupad, Jaipur", "source_provider": "local_fallback", "rating": 4.6, "price_level": 1, "open_now": True, "estimated_cost_inr": 50, "confidence": 0.95},
        {"id": "jp_amer_fort", "name": "Amer Fort", "category": "monument", "lat": 26.9855, "lng": 75.8513, "address": "Amer, Jaipur", "source_provider": "local_fallback", "rating": 4.7, "price_level": 2, "open_now": True, "estimated_cost_inr": 200, "confidence": 0.92},
        {"id": "jp_johri", "name": "Johri Bazaar", "category": "market", "lat": 26.9192, "lng": 75.8291, "address": "Johri Bazaar, Jaipur", "source_provider": "local_fallback", "rating": 4.3, "price_level": 2, "open_now": True, "estimated_cost_inr": 300, "confidence": 0.85},
        {"id": "jp_lmb", "name": "Laxmi Mishthan Bhandar", "category": "restaurant", "lat": 26.9200, "lng": 75.8252, "address": "Johri Bazaar, Jaipur", "source_provider": "local_fallback", "rating": 4.2, "price_level": 2, "open_now": True, "estimated_cost_inr": 250, "confidence": 0.82},
        {"id": "jp_city_palace", "name": "City Palace", "category": "monument", "lat": 26.9258, "lng": 75.8236, "address": "Tulsi Marg, Jaipur", "source_provider": "local_fallback", "rating": 4.5, "price_level": 2, "open_now": True, "estimated_cost_inr": 300, "confidence": 0.90},
        {"id": "jp_albert_hall", "name": "Albert Hall Museum", "category": "museum", "lat": 26.9116, "lng": 75.8195, "address": "Ram Niwas Bagh, Jaipur", "source_provider": "local_fallback", "rating": 4.4, "price_level": 1, "open_now": True, "estimated_cost_inr": 150, "confidence": 0.88},
        {"id": "jp_chokhi_dhani", "name": "Chokhi Dhani", "category": "cultural space", "lat": 26.7667, "lng": 75.8450, "address": "Tonk Road, Jaipur", "source_provider": "local_fallback", "rating": 4.3, "price_level": 3, "open_now": True, "estimated_cost_inr": 900, "confidence": 0.85},
        {"id": "jp_tapri", "name": "Tapri The Tea House", "category": "cafe", "lat": 26.9079, "lng": 75.8055, "address": "C-Scheme, Jaipur", "source_provider": "local_fallback", "rating": 4.6, "price_level": 2, "open_now": True, "estimated_cost_inr": 200, "confidence": 0.90}
    ]
}

class PlacesClient(BaseClient):
    def __init__(self):
        provider = getattr(settings, "PLACES_PROVIDER", "overpass")
        self.provider = provider.lower() if provider else "overpass"
        
        base_url = "https://overpass-api.de/api"
        super().__init__(provider_name=self.provider, base_url=base_url)

    async def search_places(self, city_geo: dict, categories: List[str], limit: int = 15, request_id: Optional[str] = None) -> List[dict]:
        city_name = city_geo.get("city", "").lower()
        lat = city_geo.get("lat")
        lng = city_geo.get("lng")
        
        # If user explicitly requested local_fallback, return right away
        if self.provider == "local_fallback":
            return self._get_local_fallback(city_name, categories, limit)
            
        if self.provider == "overpass" and lat and lng:
            try:
                # Query Overpass API dynamically
                # around:5000 is 5km radius
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
                    json_data=None, # Overpass takes data in body or parameters
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
                    
                    # Deduplicate unnamed nodes
                    if name == "Local Spot":
                        continue
                        
                    # Mapped category
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
                            
                    # Estimated cost in INR based on category
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
                        "rating": None, # Unavailable
                        "price_level": None,
                        "open_now": True,
                        "estimated_cost_inr": estimated_cost,
                        "confidence": 0.80
                    })
                
                if candidates:
                    return candidates[:limit]
            except Exception as e:
                logger.warning(f"Overpass search failed for {city_name}: {e}. Falling back to seeds.")
                
        # If overpass failed or returned nothing, try to return local fallback seeds
        return self._get_local_fallback(city_name, categories, limit)

    def _get_local_fallback(self, city_name: str, categories: List[str], limit: int) -> List[dict]:
        # Normalise city name
        resolved_city = "delhi"
        for key in LOCAL_SEEDS.keys():
            if key in city_name or city_name in key:
                resolved_city = key
                break
                
        seeds = LOCAL_SEEDS.get(resolved_city, LOCAL_SEEDS["delhi"])
        
        # Filter matching categories if necessary or just return best mix
        # Let's return the seeds directly as they are already a balanced mix
        return seeds[:limit]
