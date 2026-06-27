from app.core.config import settings
from app.integrations.otari_client import OtariClient


class RouterEngine:
    def _estimate_cost(self, model_id: str, complexity: dict, parsed: dict) -> float:
        token_count = 900 + int(complexity.get("score", 0) * 10)
        output_tokens = 900
        if parsed.get("moods", {}).get("value"):
            output_tokens += 200
        client = OtariClient()
        pricing_key = client.get_pricing_key(model_id)
        return round(client.calculate_cost(pricing_key, token_count, output_tokens), 6)

    def decide_route(self, security: dict, intent: dict, parsed: dict, complexity: dict, budget: dict, missing_fields: list) -> dict:
        if not security["safe"]:
            return {
                "route": "BLOCKED",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Security scanner blocked prompt before model execution.",
            }

        intent_type = intent["type"]
        if intent_type == "booking_request":
            return {
                "route": "OUT_OF_SCOPE",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Booking/payment requests are outside Travy planning scope.",
            }

        if intent_type == "unsupported_live_data":
            return {
                "route": "FALLBACK",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Requested live data source is not supported by the planner's factual toolchain.",
            }

        if intent_type == "budget_math":
            return {
                "route": "LOCAL_LOGIC",
                "model_tier": "local",
                "model_id": settings.LLAMAFILE_MODEL,
                "model_configured": bool(settings.LLAMAFILE_BASE_URL),
                "estimated_cost_usd": 0.0,
                "reason": "Budget calculation is handled by the local control plane.",
            }

        if missing_fields:
            return {
                "route": "CLARIFY_REQUIRED",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": f"Required planning fields are missing: {missing_fields}",
            }

        budget_mode = budget["mode"]
        comp_score = complexity["score"]
        if budget_mode == "critical":
            return {
                "route": "API_ONLY_FALLBACK",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": 0.0,
                "reason": "Budget critical: use API-only fallback and avoid Otari planning.",
            }

        if budget_mode == "low":
            model_id = settings.OTARI_CHEAP_MODEL
            tier = "cheap"
            route = "COMPRESSED_CHEAP_MODEL"
            reason = f"Low budget: compressed context with Otari cheap model for final itinerary generation."
        elif comp_score >= 60:
            model_id = settings.OTARI_STRONG_MODEL
            tier = "strong_planner"
            route = "STRONG_PLANNER_MODEL"
            reason = f"High complexity ({comp_score}): Otari strong model for multi-constraint itinerary generation."
        elif comp_score >= 35:
            model_id = settings.OTARI_BALANCED_MODEL
            tier = "balanced_planner"
            route = "BALANCED_PLANNER_MODEL"
            reason = f"Moderate complexity ({comp_score}): Otari balanced model for final itinerary generation."
        else:
            model_id = settings.OTARI_CHEAP_MODEL
            tier = "cheap"
            route = "COMPRESSED_CHEAP_MODEL"
            reason = f"Simple travel request ({comp_score}): use compressed Otari cheap model."

        cost = self._estimate_cost(model_id, complexity, parsed)
        if cost > budget.get("remaining_budget_usd", 0.0):
            return {
                "route": "BUDGET_EXCEEDED",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "estimated_cost_usd": cost,
                "reason": "Estimated Otari request cost exceeds remaining live budget.",
            }

        return {
            "route": route,
            "model_tier": tier,
            "model_id": model_id,
            "model_configured": bool(model_id),
            "estimated_cost_usd": cost,
            "reason": reason,
        }
