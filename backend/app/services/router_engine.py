from app.core.config import settings

class RouterEngine:
    def decide_route(self, security: dict, intent: dict, parsed: dict, complexity: dict, budget: dict, missing_fields: list) -> dict:
        # Check security block
        if not security["safe"]:
            return {
                "route": "BLOCKED",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Security scanner blocked prompt before model execution."
            }
            
        # Check intent types
        intent_type = intent["type"]
        if intent_type == "booking_request":
            return {
                "route": "OUT_OF_SCOPE",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Booking/payment requests are out of scope for the Travy MVP."
            }
            
        if intent_type == "unsupported_live_data":
            return {
                "route": "FALLBACK",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Guardian Route uses static proxy signals, not unsupported real-time live data."
            }
            
        # Check deterministic math before missing fields check
        if intent_type == "budget_math":
            return {
                "route": "LOCAL_LOGIC",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Simple budget calculation performed via deterministic local logic."
            }
            
        # Check missing required fields
        if missing_fields:
            return {
                "route": "CLARIFY_REQUIRED",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": f"Required planning fields are missing: {missing_fields}"
            }
            
        # Check critical budget
        budget_mode = budget["mode"]
        if budget_mode == "critical":
            return {
                "route": "API_ONLY_FALLBACK",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "AI budget is critical. Switched to API-only static fallback."
            }
            
        # Router heuristics based on complexity
        comp_score = complexity["score"]
        if comp_score < 40:
            model_id = settings.OTARI_LOCAL_LLM_MODEL
            return {
                "route": "LOCAL_LLM",
                "model_tier": "local",
                "model_id": model_id,
                "model_configured": bool(model_id),
                "estimated_cost_usd": 0.0,
                "reason": f"Low complexity request ({comp_score}) routed to local/cheap tier."
            }
            
        elif comp_score < 80:
            model_id = settings.OTARI_BALANCED_MODEL
            return {
                "route": "BALANCED_PLANNER_MODEL",
                "model_tier": "balanced_planner",
                "model_id": model_id,
                "model_configured": bool(model_id),
                "estimated_cost_usd": 0.015,
                "reason": f"Medium complexity request ({comp_score}) routed to balanced planner model."
            }
            
        else:  # High complexity >= 80
            if budget_mode == "low":
                model_id = settings.OTARI_CHEAP_MODEL
                return {
                    "route": "COMPRESSED_CHEAP_MODEL",
                    "model_tier": "cheap",
                    "model_id": model_id,
                    "model_configured": bool(model_id),
                    "estimated_cost_usd": 0.008,
                    "reason": f"High complexity ({comp_score}) but low budget: compressed context and cheap model."
                }
            else:  # healthy/auto
                model_id = settings.OTARI_STRONG_MODEL
                return {
                    "route": "STRONG_PLANNER_MODEL",
                    "model_tier": "strong_planner",
                    "model_id": model_id,
                    "model_configured": bool(model_id),
                    "estimated_cost_usd": 0.041,
                    "reason": "Complex group planning with budget, route ordering, mood, and fatigue constraints."
                }
