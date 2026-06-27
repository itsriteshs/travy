class ComplexityService:
    def calculate(self, parsed: dict, overall_parser_confidence: float = 1.0) -> dict:
        score = 0
        breakdown = []
        
        def get_val(field):
            if not parsed:
                return None
            val_obj = parsed.get(field)
            if isinstance(val_obj, dict) and "value" in val_obj:
                return val_obj["value"]
            return val_obj

        # 1. Mood count complexity (+10 per mood)
        moods = get_val("moods") or []
        if moods:
            pts = len(moods) * 10
            score += pts
            breakdown.append({
                "feature": "moods",
                "points": pts,
                "reason": f"{len(moods)} moods requested."
            })
            
        # 2. Group size complexity (+5 per extra person)
        group_size = get_val("group_size") or 1
        if group_size > 1:
            pts = (group_size - 1) * 5
            score += pts
            breakdown.append({
                "feature": "group_size",
                "points": pts,
                "reason": f"Group size is {group_size}."
            })
            
        # 3. Fatigue constraint (+20 if low energy)
        energy = get_val("energy")
        if energy == "low" or (isinstance(energy, str) and "low" in energy):
            score += 20
            breakdown.append({
                "feature": "energy",
                "points": 20,
                "reason": "Fatigue-aware low energy preference specified."
            })
            
        # 4. Gaps/Ambiguity complexity (+15 if gaps > 2)
        gaps = get_val("gaps")
        if not gaps:
            # calculate missing required fields from parsed dictionary keys
            gaps = []
            for field in ["city", "group_size", "budget_per_person_inr", "start_time", "end_time", "moods"]:
                if not get_val(field):
                    gaps.append(field)
        if len(gaps) > 2:
            score += 15
            breakdown.append({
                "feature": "ambiguity",
                "points": 15,
                "reason": f"{len(gaps)} missing constraints (gaps)."
            })
            
        # 5. Crowd tolerance complexity (+10 if low crowd tolerance)
        crowd_tolerance = get_val("crowd_tolerance")
        if crowd_tolerance == "low":
            score += 10
            breakdown.append({
                "feature": "crowd_tolerance",
                "points": 10,
                "reason": "Low crowd tolerance requested."
            })
            
        score = min(score, 100)
        
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
