import logging
from typing import List, Dict, Any, Optional
from app.integrations.distance_client import DistanceClient

logger = logging.getLogger("travy.route_optimizer_service")

class RouteOptimizerService:
    def __init__(self):
        self.distance_client = DistanceClient()

    async def optimize_route(
        self,
        stops: List[Dict[str, Any]],
        start_lat: float,
        start_lng: float,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not stops:
            return {"ordered_stops": [], "route_ordering": {"method": "none", "confidence": 0.0}, "total_travel_time_minutes": 0}
            
        # We build coordinates list for the distance matrix call
        # Origin 0 is the start location
        locations = [{"lat": start_lat, "lng": start_lng}] + [{"lat": s["lat"], "lng": s["lng"]} for s in stops]
        
        # Query matrix
        matrix = await self.distance_client.get_distance_matrix(locations, locations, request_id)
        
        provider = matrix.get("provider", "local_haversine")
        status = matrix.get("status", "fallback")
        warning = matrix.get("warning")
        
        # Simple Nearest Neighbor heuristic starting from Index 0 (Start Location)
        unvisited = list(range(1, len(locations)))
        current_idx = 0
        ordered_indices = []
        total_time_seconds = 0
        total_distance_meters = 0
        
        rows = matrix.get("rows", [])
        
        while unvisited:
            best_next = None
            min_duration = float("inf")
            best_dist = 0
            
            # Find closest unvisited element
            for u in unvisited:
                # Row current_idx, element u
                try:
                    elem = rows[current_idx]["elements"][u]
                    if elem.get("status") == "OK":
                        dur = elem.get("duration_value_seconds", 3600)
                        dist = elem.get("distance_value_meters", 10000)
                        if dur < min_duration:
                            min_duration = dur
                            best_next = u
                            best_dist = dist
                except Exception:
                    pass
                    
            if best_next is None:
                # Fallback if matrix row is missing
                best_next = unvisited[0]
                min_duration = 600 # 10 mins fallback
                best_dist = 5000 # 5km
                
            total_time_seconds += min_duration
            total_distance_meters += best_dist
            current_idx = best_next
            ordered_indices.append(best_next - 1) # Convert back to stops index
            unvisited.remove(best_next)
            
        ordered_stops = [stops[i] for i in ordered_indices]
        
        # Add stop numbers and routing trace information
        for idx, stop in enumerate(ordered_stops):
            stop["stop_number"] = idx + 1
            
        confidence = 0.90 if provider == "google_maps" else 0.55
        
        route_ordering = {
            "method": "maps_distance_matrix" if provider == "google_maps" else "haversine_estimate",
            "provider": provider,
            "confidence": confidence,
            "total_distance_meters": total_distance_meters
        }
        if warning:
            route_ordering["warning"] = warning
            
        return {
            "ordered_stops": ordered_stops,
            "route_ordering": route_ordering,
            "total_travel_time_minutes": int(total_time_seconds / 60)
        }
