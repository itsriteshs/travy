import logging
import re
from typing import List, Dict, Any, Optional
from app.integrations.distance_client import DistanceClient

logger = logging.getLogger("travy.route_optimizer_service")

class RouteOptimizerService:
    def __init__(self):
        self.distance_client = DistanceClient()

    def _parse_time_to_minutes(self, t_str: str) -> int:
        t_str = t_str.upper().strip()
        match = re.search(r'(\d+)\s*(AM|PM)', t_str)
        if not match:
            return 600 # 10 AM default
        hour = int(match.group(1))
        period = match.group(2)
        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0
        return hour * 60

    async def optimize_route(
        self,
        stops: List[Dict[str, Any]],
        start_lat: float,
        start_lng: float,
        start_time_str: str = "10 AM",
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not stops:
            return {
                "ordered_stops": [],
                "route_ordering": {"method": "none", "confidence": 0.0},
                "total_travel_time_minutes": 0
            }
            
        # Build coordinates list for Distance Matrix API
        locations = [{"lat": start_lat, "lng": start_lng}] + [{"lat": s["lat"], "lng": s["lng"]} for s in stops]
        matrix = await self.distance_client.get_distance_matrix(locations, locations, request_id)
        
        provider = matrix.get("provider", "local_haversine")
        rows = matrix.get("rows", [])
        
        # Heuristic optimization tracking variables
        unvisited = list(range(1, len(locations)))
        current_idx = 0
        ordered_indices = []
        total_time_seconds = 0
        total_distance_meters = 0
        
        current_time_mins = self._parse_time_to_minutes(start_time_str)
        cumulative_fatigue = 20.0 # start baseline fatigue
        
        while unvisited:
            best_next = None
            highest_rank_score = -float("inf")
            best_dur = 0
            best_dist = 0
            
            # Lunch window: 12 PM (720m) to 2 PM (840m)
            # Dinner window: 7 PM (1140m) to 9 PM (1260m)
            is_meal_time = (720 <= current_time_mins <= 840) or (1140 <= current_time_mins <= 1260)
            
            for u in unvisited:
                stop_ref = stops[u - 1]
                category = stop_ref.get("category", "sightseeing").lower()
                
                # Fetch travel distance / duration from matrix
                dur = 600
                dist = 5000
                try:
                    elem = rows[current_idx]["elements"][u]
                    if elem.get("status") == "OK":
                        dur = elem.get("duration_value_seconds", 600)
                        dist = elem.get("distance_value_meters", 5000)
                except Exception:
                    pass
                
                # Heuristic rank score (higher is better)
                # 1. Distance penalty (lower duration is better)
                score = - (dur / 60.0) * 1.5
                
                # 2. Meal time alignment
                if is_meal_time and category in ["food", "cafe", "restaurant"]:
                    score += 50.0 # prioritize dining stop during meal times
                    
                # 3. Fatigue management
                is_high_energy = category in ["market", "shopping street", "monument"]
                if cumulative_fatigue > 60.0:
                    if category in ["cafe", "restaurant", "chill"]:
                        score += 30.0 # prioritize resting stops
                    elif is_high_energy:
                        score -= 20.0 # penalize high energy stops
                else:
                    if is_high_energy:
                        score += 10.0 # can do active exploring when fresh
                
                if score > highest_rank_score:
                    highest_rank_score = score
                    best_next = u
                    best_dur = dur
                    best_dist = dist
            
            if best_next is None:
                best_next = unvisited[0]
                best_dur = 600
                best_dist = 5000
                
            # Simulate transition
            total_time_seconds += best_dur
            total_distance_meters += best_dist
            current_idx = best_next
            
            # Add stop duration of 90 minutes + travel time
            current_time_mins += int(best_dur / 60.0) + 90
            
            # Fatigue accumulation update
            next_stop_cat = stops[best_next - 1].get("category", "sightseeing").lower()
            if next_stop_cat in ["cafe", "restaurant", "chill"]:
                cumulative_fatigue = max(10.0, cumulative_fatigue - 20.0)
            else:
                cumulative_fatigue = min(100.0, cumulative_fatigue + 25.0)
                
            ordered_indices.append(best_next - 1)
            unvisited.remove(best_next)
            
        ordered_stops = [stops[i] for i in ordered_indices]
        for idx, stop in enumerate(ordered_stops):
            stop["stop_number"] = idx + 1
            
        confidence = 0.90 if provider == "google_maps" else 0.55
        route_ordering = {
            "method": "constraint_tsp_search",
            "provider": provider,
            "confidence": confidence,
            "total_distance_meters": total_distance_meters
        }
        
        return {
            "ordered_stops": ordered_stops,
            "route_ordering": route_ordering,
            "total_travel_time_minutes": int(total_time_seconds / 60)
        }
