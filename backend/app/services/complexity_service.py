class ComplexityService:
    def calculate(self, parsed: dict, overall_parser_confidence: float) -> dict:
        score = 0
        breakdown = []
        
        # Group size
        group_size = parsed.get("group_size", {}).get("value")
        if group_size and group_size > 1:
            score += 20
            breakdown.append({
                "feature": "group_planning",
                "points": 20,
                "reason": f"Group size is {group_size} (> 1)."
            })
            
        # Budget constraint
        budget = parsed.get("budget_per_person_inr", {}).get("value")
        if budget:
            score += 15
            breakdown.append({
                "feature": "budget_constraint",
                "points": 15,
                "reason": f"Budget per person is specified: ₹{budget}."
            })
            
        # Time window
        start = parsed.get("start_time", {}).get("value")
        end = parsed.get("end_time", {}).get("value")
        if start and end:
            score += 15
            breakdown.append({
                "feature": "time_window",
                "points": 15,
                "reason": f"Time window is specified: {start} to {end}."
            })
            
        # Multiple moods
        moods = parsed.get("moods", {}).get("value") or []
        if len(moods) > 2:
            score += 15
            breakdown.append({
                "feature": "multiple_moods",
                "points": 15,
                "reason": f"More than two moods are requested: {moods}."
            })
            
        # Route ordering
        if len(moods) > 1 and start and end:
            score += 15
            breakdown.append({
                "feature": "route_ordering",
                "points": 15,
                "reason": "Multiple stops need ordering within the time window."
            })
            
        # Fatigue constraint
        energy = parsed.get("energy", {}).get("value")
        if energy in ["medium-low", "high"]:
            score += 8
            breakdown.append({
                "feature": "fatigue_constraint",
                "points": 8,
                "reason": f"Fatigue preference is specified: {energy}."
            })
            
        # Parser uncertainty
        if overall_parser_confidence < 0.95:
            score += 3
            breakdown.append({
                "feature": "parser_uncertainty",
                "points": 3,
                "reason": "Some soft preferences are inferred."
            })
            
        # Level determination
        if score >= 80:
            level = "high"
        elif score >= 50:
            level = "medium"
        else:
            level = "low"
            
        return {
            "score": score,
            "level": level,
            "breakdown": breakdown
        }
