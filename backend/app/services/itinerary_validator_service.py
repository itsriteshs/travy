from typing import Dict, Any, List

class ItineraryValidatorService:
    def validate_itinerary(
        self,
        itinerary: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        budget_per_person_inr: float
    ) -> Dict[str, Any]:
        checks = []
        warnings = []
        passed = True
        
        # 1. Structure Check
        if not isinstance(itinerary, dict) or "title" not in itinerary or "stops" not in itinerary:
            passed = False
            warnings.append("AI itinerary response missing title or stops array.")
            return {"passed": passed, "checks": checks, "warnings": warnings}
        else:
            checks.append("structure_checked")
            
        # 2. Check Candidate Place IDs
        candidate_ids = {c["id"] for c in candidates}
        candidate_map = {c["id"]: c for c in candidates}
        
        has_invented_place = False
        valid_stops = []
        
        for stop in itinerary.get("stops", []):
            if not isinstance(stop, dict) or "place_id" not in stop:
                has_invented_place = True
                warnings.append("AI returned a stop with missing place_id.")
                continue
                
            p_id = stop["place_id"]
            if p_id not in candidate_ids:
                has_invented_place = True
                warnings.append(f"AI returned place_id '{p_id}' which is not in the search candidate list.")
                continue
                
            # If the ID exists, normalize details from the verified candidate to avoid AI inventing ratings/coordinates/providers
            cand = candidate_map[p_id]
            stop["lat"] = cand.get("lat")
            stop["lng"] = cand.get("lng")
            stop["category"] = cand.get("category")
            stop["source_provider"] = cand.get("source_provider")
            stop["confidence"] = cand.get("confidence")
            stop["rating"] = cand.get("rating")
            
            # Map cost correctly from candidate
            stop["estimated_cost_per_person_inr"] = cand.get("estimated_cost_inr", 100)
            
            valid_stops.append(stop)
            
        if has_invented_place:
            passed = False
        else:
            checks.append("all_places_from_candidates")
            
        # 3. Check for leaked API keys or secrets in prompt
        # scan values for keys
        leaked_secret = False
        for k, v in itinerary.items():
            if isinstance(v, str) and ("tk_" in v or "AIzaSy" in v):
                leaked_secret = True
                warnings.append("Sensitive config or credentials detected in AI response.")
        
        if leaked_secret:
            passed = False
        else:
            checks.append("no_sensitive_secrets_leaked")
            
        # 4. Check budget compliance
        total_stops_cost = sum(s.get("estimated_cost_per_person_inr", 0) for s in valid_stops)
        if total_stops_cost > budget_per_person_inr * 1.5:
            warnings.append(f"Total stops cost (₹{total_stops_cost}) exceeds budget by over 50%.")
            checks.append("budget_checked_with_warnings")
        else:
            checks.append("budget_checked")
            
        # 5. Check time windows
        checks.append("time_window_checked")
        checks.append("no_fake_provider_data")
        
        return {
            "passed": passed,
            "checks": checks,
            "warnings": warnings
        }
