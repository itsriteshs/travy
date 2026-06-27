import math
import logging
from typing import List, Dict, Any, Optional
from app.services.place_provider_service import PlaceProviderService

logger = logging.getLogger("travy.candidate_builder_service")

MOOD_CATEGORY_MAP = {
    "shopping": ["market", "mall", "bazaar", "shopping street"],
    "food": ["restaurant", "cafe", "street food", "food court"],
    "photos": ["monument", "viewpoint", "garden", "art gallery", "landmark"],
    "chill": ["cafe", "park", "lake", "bookstore", "garden"],
    "sightseeing": ["monument", "museum", "heritage site", "cultural space"],
    "music": ["venue", "event space", "cultural center"],
    "events": ["venue", "event space", "cultural center"]
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000 # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class CandidateBuilderService:
    def __init__(self):
        self.place_provider = PlaceProviderService()

    def build_categories(self, moods: List[str]) -> List[str]:
        categories = set()
        for mood in moods:
            mood_lower = mood.lower().strip()
            # Direct mapping
            mapped = MOOD_CATEGORY_MAP.get(mood_lower, [mood_lower])
            for cat in mapped:
                categories.add(cat)
        return list(categories)

    async def get_candidates(self, city_geo: dict, moods: List[str], request_id: Optional[str] = None) -> Dict[str, Any]:
        categories = self.build_categories(moods)
        
        # Query places client
        raw_places = await self.place_provider.search_places(
            city_geo=city_geo,
            categories=categories,
            limit=25,
            request_id=request_id
        )
        
        raw_count = len(raw_places)
        deduped = self.deduplicate(raw_places)
        deduped_count = len(deduped)
        
        return {
            "candidates": deduped,
            "raw_candidates_count": raw_count,
            "deduped_candidates_count": deduped_count,
            "duplicates_removed": raw_count - deduped_count,
            "categories_searched": categories
        }

    def deduplicate(self, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped = []
        for p in places:
            is_dup = False
            p_name = p["name"].lower().strip()
            p_lat = p["lat"]
            p_lng = p["lng"]
            
            for existing in deduped:
                e_name = existing["name"].lower().strip()
                e_lat = existing["lat"]
                e_lng = existing["lng"]
                
                # Check Jaccard similarity / name similarity
                name_overlap = False
                if p_name == e_name:
                    name_overlap = True
                else:
                    # check abbreviation / substrings e.g. "cp delhi" vs "connaught place"
                    # simple word intersection
                    p_words = set(p_name.split())
                    e_words = set(e_name.split())
                    common = p_words.intersection(e_words)
                    # ignore common city keywords
                    common.discard("delhi")
                    common.discard("bangalore")
                    common.discard("jaipur")
                    if len(common) >= 2 or (len(p_words) == 1 and p_name in e_name) or (len(e_words) == 1 and e_name in p_name):
                        name_overlap = True
                        
                # Check distance (under 150m)
                dist = haversine_distance(p_lat, p_lng, e_lat, e_lng)
                
                # If they have name overlap and are under 150m, or are VERY close (under 30m)
                if (name_overlap and dist < 150.0) or dist < 30.0:
                    is_dup = True
                    # Keep the one with higher rating / provider confidence
                    if p.get("rating") and not existing.get("rating"):
                        existing.update(p)
                    break
                    
            if not is_dup:
                deduped.append(p)
                
        return deduped
