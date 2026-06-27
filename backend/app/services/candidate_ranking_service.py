import math
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("travy.candidate_ranking_service")

class CandidateRankingService:
    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        city_geo: Dict[str, Any],
        parsed_constraints: Dict[str, Any],
        weather_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Load weights from config files
        weights = settings.weights
        
        center_lat = city_geo.get("lat", 0.0)
        center_lng = city_geo.get("lng", 0.0)
        
        # Extract constraints safely
        budget_per_person = parsed_constraints.get("budget_per_person_inr", {}).get("value") or 1000.0
        group_size = parsed_constraints.get("group_size", {}).get("value") or 1
        energy_preference = parsed_constraints.get("energy", {}).get("value") or "medium"
        transport_method = parsed_constraints.get("transport", {}).get("value") or "mixed"
        moods = parsed_constraints.get("moods", {}).get("value") or ["sightseeing"]
        crowd_tolerance = parsed_constraints.get("crowd_tolerance", {}).get("value") or "medium"
        safety_preferences = parsed_constraints.get("safety_preferences", {}).get("value") or "standard"
        
        # Available minutes
        start_time_str = parsed_constraints.get("start_time", {}).get("value") or "10 AM"
        end_time_str = parsed_constraints.get("end_time", {}).get("value") or "6 PM"
        
        def _time_to_minutes(t_str: str) -> int:
            t_str = t_str.upper().strip()
            match = re.search(r'(\d+)\s*(AM|PM)', t_str)
            if not match:
                return 600
            hour = int(match.group(1))
            period = match.group(2)
            if period == "PM" and hour != 12:
                hour += 12
            elif period == "AM" and hour == 12:
                hour = 0
            return hour * 60

        import re
        duration_minutes = max(60, _time_to_minutes(end_time_str) - _time_to_minutes(start_time_str))
        
        # Meteorological parameters
        temperature = weather_data.get("temperature", 25.0)
        humidity = weather_data.get("humidity", 50.0)
        weather_code = weather_data.get("weather_code", 0)
        
        ranked = []
        
        for c in candidates:
            # Place coordinates and info
            p_lat = c.get("lat", center_lat)
            p_lng = c.get("lng", center_lng)
            cost = c.get("estimated_cost_inr", 100.0)
            category = c.get("category", "sightseeing").lower()
            rating = c.get("rating")
            review_count = c.get("review_count") or 15
            open_now = c.get("open_now", True)
            
            # Calculate distance using Haversine
            from app.services.candidate_builder_service import haversine_distance
            dist_km = haversine_distance(p_lat, p_lng, center_lat, center_lng) / 1000.0
            
            # 1. budget_fit (continuous Sigmoid decay)
            # The closer or lower the cost is compared to budget_per_person, the higher the score
            if budget_per_person > 0:
                cost_diff = cost - budget_per_person
                budget_fit = 100.0 / (1.0 + math.exp(cost_diff / (budget_per_person * 0.25)))
            else:
                budget_fit = 100.0
                
            # 2. distance_fit (continuous linear decay)
            distance_fit = max(0.0, 100.0 - dist_km * 7.5)
            
            # 3. time_fit (based on trip duration minutes)
            # Single stop duration is typically 90m
            time_fit = max(0.0, 100.0 - abs((90.0 / duration_minutes) - 0.25) * 100.0)
            
            # 4. weather_fit (dynamic index comfort)
            is_outdoor = category in ["garden", "park", "viewpoint", "monument"]
            comfort_diff = abs(temperature - 22.0)
            if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: # Rainy
                comfort_diff += 25.0 # penalty for rain
            weather_fit = max(0.0, 100.0 - (comfort_diff * 3.5 if is_outdoor else comfort_diff * 1.0))
            
            # 5. group_fit (capacity fit)
            if category in ["cafe", "bookstore"]:
                group_fit = max(20.0, 100.0 - (group_size * 4.0))
            else:
                group_fit = min(100.0, 80.0 + (group_size * 1.5))
                
            # 6. mood_fit (category overlap with preferences)
            matches = 0
            from app.services.candidate_builder_service import MOOD_CATEGORY_MAP
            for mood in moods:
                mapped_cats = MOOD_CATEGORY_MAP.get(mood.lower(), [mood.lower()])
                if category in mapped_cats:
                    matches += 1
            mood_fit = (matches / len(moods) * 100.0) if moods else 75.0
            
            # 7. opening_hours_fit (opening status logic)
            base_hours_fit = 95.0 if open_now else 20.0
            opening_hours_fit = min(100.0, base_hours_fit + (rating or 4.0))
            
            # 8. safety_fit (comfort proxies)
            safety_multiplier = 4.0 if safety_preferences == "high_comfort" else 2.0
            safety_fit = min(100.0, 80.0 + (rating or 4.0) * safety_multiplier)
            
            # 9. crowd_fit (tolerance matching)
            # Popular slots with high review count are penalized for low tolerance
            if crowd_tolerance == "low":
                crowd_fit = max(10.0, 100.0 - math.log1p(review_count) * 12.0)
            else:
                crowd_fit = min(100.0, 70.0 + math.log1p(review_count) * 3.0)
                
            # 10. fatigue_penalty (pace mismatch)
            is_active_place = category in ["market", "shopping street", "monument"]
            if "low" in energy_preference and is_active_place:
                fatigue_penalty = 25.0 + (cost % 5)
            elif "high" in energy_preference and not is_active_place:
                fatigue_penalty = 12.0 + (cost % 3)
            else:
                fatigue_penalty = 4.0 + (cost % 2)
                
            # 11. transport_fit (transport method suitability)
            if transport_method == "walk":
                transport_fit = max(0.0, 100.0 - dist_km * 25.0)
            else:
                transport_fit = max(0.0, 100.0 - dist_km * 4.0)
                
            # Compute total weighted score
            weighted_scores = {
                "budget_fit": budget_fit * weights.get("budget_fit", 0.15),
                "distance_fit": distance_fit * weights.get("distance_fit", 0.10),
                "time_fit": time_fit * weights.get("time_fit", 0.10),
                "weather_fit": weather_fit * weights.get("weather_fit", 0.10),
                "group_fit": group_fit * weights.get("group_fit", 0.10),
                "mood_fit": mood_fit * weights.get("mood_fit", 0.15),
                "opening_hours_fit": opening_hours_fit * weights.get("opening_hours_fit", 0.10),
                "safety_fit": safety_fit * weights.get("safety_fit", 0.10),
                "crowd_fit": crowd_fit * weights.get("crowd_fit", 0.05),
                "transport_fit": transport_fit * weights.get("transport_fit", 0.05)
            }
            
            # Subtract weighted fatigue penalty
            total_score = sum(weighted_scores.values()) - (fatigue_penalty * weights.get("fatigue_penalty", 0.05))
            
            # Assemble score breakdown with explanations
            score_breakdown = [
                {"feature": "budget_fit", "points": int(budget_fit), "reason": f"Sigmoid fit score {budget_fit:.1f}/100 based on price ₹{cost} vs budget ₹{budget_per_person}."},
                {"feature": "distance_fit", "points": int(distance_fit), "reason": f"Distance decay fit {distance_fit:.1f}/100 for {dist_km:.2f}km separation."},
                {"feature": "time_fit", "points": int(time_fit), "reason": f"Timing allocation match {time_fit:.1f}/100 for duration {duration_minutes}m."},
                {"feature": "weather_fit", "points": int(weather_fit), "reason": f"Weather comfort fit {weather_fit:.1f}/100 at temperature {temperature}°C."},
                {"feature": "group_fit", "points": int(group_fit), "reason": f"Group sizing index {group_fit:.1f}/100 matching {group_size} travelers."},
                {"feature": "mood_fit", "points": int(mood_fit), "reason": f"Mood alignment matches {matches} preferences."},
                {"feature": "opening_hours_fit", "points": int(opening_hours_fit), "reason": f"Opening timeframe safety index {opening_hours_fit:.1f}/100."},
                {"feature": "safety_fit", "points": int(safety_fit), "reason": f"Safety proxy comfort match {safety_fit:.1f}/100."},
                {"feature": "crowd_fit", "points": int(crowd_fit), "reason": f"Crowd tolerance index {crowd_fit:.1f}/100."},
                {"feature": "fatigue_fit", "points": int(100 - fatigue_penalty), "reason": f"Fatigue penalty subtraction {fatigue_penalty:.1f} for {energy_preference} pace."},
                {"feature": "transport_fit", "points": int(transport_fit), "reason": f"Transport compatibility index {transport_fit:.1f}/100 for {transport_method}."}
            ]
            
            ranked_item = c.copy()
            ranked_item["total_score"] = round(total_score, 2)
            ranked_item["score_breakdown"] = score_breakdown
            ranked.append(ranked_item)
            
        ranked.sort(key=lambda x: x["total_score"], reverse=True)
        return ranked
