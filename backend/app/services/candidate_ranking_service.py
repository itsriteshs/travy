import math
from typing import List, Dict, Any, Optional

class CandidateRankingService:
    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        city_geo: Dict[str, Any],
        moods: List[str],
        budget_per_person_inr: float,
        energy_preference: str
    ) -> List[Dict[str, Any]]:
        ranked = []
        center_lat = city_geo.get("lat", 0.0)
        center_lng = city_geo.get("lng", 0.0)
        
        for c in candidates:
            score_breakdown = []
            
            # 1. Mood Match (Max 30)
            mood_points = 0
            matched_moods = []
            place_cat = c.get("category", "").lower()
            
            # Map place category to moods
            # shopping -> market, mall, bazaar, shopping street
            # food -> restaurant, cafe, street food, food court
            # photos -> monument, viewpoint, garden, art gallery, landmark
            for mood in moods:
                m_lower = mood.lower().strip()
                if m_lower == "shopping" and place_cat in ["market", "mall", "bazaar", "shopping street"]:
                    mood_points += 15
                    matched_moods.append(mood)
                elif m_lower == "food" and place_cat in ["restaurant", "cafe", "street food", "food court"]:
                    mood_points += 15
                    matched_moods.append(mood)
                elif m_lower == "photos" and place_cat in ["monument", "viewpoint", "garden", "art gallery", "landmark"]:
                    mood_points += 15
                    matched_moods.append(mood)
                elif m_lower == "chill" and place_cat in ["cafe", "park", "lake", "bookstore", "garden"]:
                    mood_points += 15
                    matched_moods.append(mood)
                elif m_lower == "sightseeing" and place_cat in ["monument", "museum", "heritage site", "cultural space", "cultural center"]:
                    mood_points += 15
                    matched_moods.append(mood)
            
            mood_points = min(mood_points, 30)
            # Default points for some relevance
            if mood_points == 0:
                mood_points = 10
                reason = f"Baseline relevance score for category {place_cat}."
            else:
                reason = f"Matches {', '.join(matched_moods)} preferences."
            score_breakdown.append({"feature": "mood_match", "points": mood_points, "reason": reason})
            
            # 2. Budget Fit (Max 20)
            cost = c.get("estimated_cost_inr", 100)
            if cost <= budget_per_person_inr:
                budget_points = 20
                reason = f"Estimated cost ₹{cost}/person fits budget of ₹{budget_per_person_inr}."
            elif cost <= budget_per_person_inr * 1.5:
                budget_points = 10
                reason = f"Estimated cost ₹{cost}/person is slightly above budget of ₹{budget_per_person_inr}."
            else:
                budget_points = 2
                reason = f"Estimated cost ₹{cost}/person exceeds budget of ₹{budget_per_person_inr}."
            score_breakdown.append({"feature": "budget_fit", "points": budget_points, "reason": reason})
            
            # 3. Distance Efficiency (Max 15)
            # Distance from center
            from app.services.candidate_builder_service import haversine_distance
            dist = haversine_distance(c["lat"], c["lng"], center_lat, center_lng) / 1000.0 # km
            if dist < 2.0:
                dist_points = 15
                reason = "Located under 2km from center, highly efficient."
            elif dist < 5.0:
                dist_points = 12
                reason = f"Located {dist:.1f}km from center, easy travel."
            elif dist < 10.0:
                dist_points = 8
                reason = f"Located {dist:.1f}km from center, moderate travel."
            else:
                dist_points = 4
                reason = f"Located {dist:.1f}km from center, longer travel required."
            score_breakdown.append({"feature": "distance_efficiency", "points": dist_points, "reason": reason})
            
            # 4. Open Status (Max 10)
            open_points = 10 if c.get("open_now", True) else 2
            reason = "Place is currently open." if open_points == 10 else "Opening hours might conflict."
            score_breakdown.append({"feature": "open_status", "points": open_points, "reason": reason})
            
            # 5. Rating or Popularity (Max 10)
            rating = c.get("rating")
            if rating:
                rating_points = int(rating * 2)
                reason = f"Highly rated at {rating}/5 by visitors."
            else:
                rating_points = 7
                reason = "Popular location with standard rating."
            score_breakdown.append({"feature": "rating_or_popularity", "points": rating_points, "reason": reason})
            
            # 6. Photo Friendliness (Max 5)
            if place_cat in ["monument", "viewpoint", "garden", "landmark"]:
                photo_points = 5
                reason = "Outstanding photo spots and scenery."
            elif place_cat in ["market", "cafe", "cultural space"]:
                photo_points = 3
                reason = "Good photo potential."
            else:
                photo_points = 1
                reason = "Standard photo opportunities."
            score_breakdown.append({"feature": "photo_friendliness", "points": photo_points, "reason": reason})
            
            # 7. Fatigue Fit (Max 5)
            fatigue_points = 3
            energy = energy_preference.lower()
            if "low" in energy:
                if place_cat in ["cafe", "restaurant", "garden", "chill"]:
                    fatigue_points = 5
                    reason = "Low walking required, fits relaxed pace."
                else:
                    fatigue_points = 2
                    reason = "Requires moderate walking."
            elif "high" in energy:
                if place_cat in ["market", "monument", "museum"]:
                    fatigue_points = 5
                    reason = "Active explore matches high energy preference."
                else:
                    fatigue_points = 3
                    reason = "Fits standard energy level."
            else:
                fatigue_points = 4
                reason = "Comfortable walking segments."
            score_breakdown.append({"feature": "fatigue_fit", "points": fatigue_points, "reason": reason})
            
            # 8. Provider Confidence (Max 5)
            conf = c.get("confidence", 0.8)
            conf_points = int(conf * 5)
            reason = f"Verified coordinates from {c.get('source_provider')}."
            score_breakdown.append({"feature": "provider_confidence", "points": conf_points, "reason": reason})
            
            total_score = sum(item["points"] for item in score_breakdown)
            
            # Add to ranked set
            ranked_item = c.copy()
            ranked_item["total_score"] = total_score
            ranked_item["score_breakdown"] = score_breakdown
            ranked.append(ranked_item)
            
        # Sort by total score descending
        ranked.sort(key=lambda x: x["total_score"], reverse=True)
        return ranked
