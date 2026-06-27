class ContextService:
    def select_context(self, budget_mode: str) -> dict:
        all_context = [
            {"key": "city", "priority": "P1", "reason": "Required for place lookup.", "estimated_tokens": 10},
            {"key": "time_window", "priority": "P1", "reason": "Required for route ordering.", "estimated_tokens": 15},
            {"key": "budget_per_person", "priority": "P1", "reason": "Hard cost constraint.", "estimated_tokens": 10},
            {"key": "group_size", "priority": "P1", "reason": "Needed for group planning.", "estimated_tokens": 10},
            {"key": "moods", "priority": "P2", "reason": "Needed for matching activities.", "estimated_tokens": 20},
            {"key": "energy", "priority": "P2", "reason": "Needed to reduce fatigue.", "estimated_tokens": 15},
            {"key": "transport", "priority": "P2", "reason": "Needed for routing transport constraints.", "estimated_tokens": 15},
            {"key": "crowd_tolerance", "priority": "P2", "reason": "Needed for crowding constraints.", "estimated_tokens": 15},
            {"key": "weather_placeholder", "priority": "P2", "reason": "Required placeholder for weather check.", "estimated_tokens": 30},
            {"key": "friend_preferences", "priority": "P3", "reason": "Useful because budget is healthy.", "estimated_tokens": 100},
            {"key": "past_liked_places", "priority": "P3", "reason": "Useful to match past preferences.", "estimated_tokens": 150},
            {"key": "short_reviews", "priority": "P3", "reason": "Improves review context.", "estimated_tokens": 150},
            {"key": "long_reviews", "priority": "P4", "reason": "High token cost and low priority.", "estimated_tokens": 800},
            {"key": "photos", "priority": "P4", "reason": "Not needed in Phase 2 analysis.", "estimated_tokens": 500},
            {"key": "old_history", "priority": "P4", "reason": "Unrelated past history records.", "estimated_tokens": 1200}
        ]
        
        included = []
        dropped = []
        tokens_saved = 0
        
        for item in all_context:
            priority = item["priority"]
            is_included = False
            
            if budget_mode == "healthy":
                if priority in ["P1", "P2", "P3"]:
                    is_included = True
            elif budget_mode == "low":
                if priority in ["P1", "P2"]:
                    is_included = True
            elif budget_mode == "critical":
                if priority in ["P1"]:
                    is_included = True
            else:  # default healthy
                if priority in ["P1", "P2", "P3"]:
                    is_included = True
                    
            if is_included:
                included.append({
                    "key": item["key"],
                    "priority": priority,
                    "reason": item["reason"]
                })
            else:
                dropped.append({
                    "key": item["key"],
                    "priority": priority,
                    "reason": item["reason"]
                })
                tokens_saved += item["estimated_tokens"]
                
        mode = "full_context" if budget_mode == "healthy" else ("low_budget" if budget_mode == "low" else "critical_budget")
        if budget_mode == "critical":
            mode = "api_only_fallback"
            
        return {
            "mode": mode,
            "included": included,
            "dropped": dropped,
            "estimated_tokens_saved": tokens_saved
        }
