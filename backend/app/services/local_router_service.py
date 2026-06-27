import json
from typing import Dict, List, Optional

from app.core.config import settings
from app.integrations.encoderfile_client import EncoderfileClient
from app.integrations.llamafile_client import LlamafileClient
from app.integrations.otari_client import OtariClient


ROUTER_SYSTEM_PROMPT = """You are Travy's local model selection agent.
Return only JSON with keys:
    selected_route: "OTARI" | "API_ONLY" | "LOCAL_MODEL" | "BLOCKED" | "CLARIFY_REQUIRED" | "BUDGET_EXCEEDED" | "OUT_OF_SCOPE"
    selected_model_id: "provider:model_name" | null
    model_tier: "strong_planner" | "balanced_planner" | "cheap" | "local" | "none"
    confidence: <0.0-1.0>
    estimated_cost_usd: <number>
    reason: <string>
If planning is required, choose the best Otari planner model for the final itinerary generation.
If required planning fields are missing, still assign a planner model if the prompt can be analyzed.
If this is a factual or API-only request, return API_ONLY or LOCAL_MODEL.
Do not invent hidden information or exceed budget without a clear reason.
"""

MODEL_TIER_ROUTE_MAP = {
        "strong_planner": "STRONG_PLANNER_MODEL",
        "balanced_planner": "BALANCED_PLANNER_MODEL",
        "cheap": "COMPRESSED_CHEAP_MODEL",
        "local": "LOCAL_LOGIC"
}


class LocalRouterService:
    def __init__(self):
        self.llamafile = LlamafileClient()
        self.encoderfile = EncoderfileClient()

    async def decide(self, features: Dict) -> Dict:
        local = await self.llamafile.structured_json(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            user_payload=features,
            timeout=45.0,
        )
        if local:
            selected_route = str(local.get("selected_route", "OTARI")).upper()
            model_tier = str(local.get("model_tier", "cheap"))
            model_id = self._normalize_model_id(local.get("selected_model_id"), model_tier)
            route = self._normalize_route(selected_route, model_tier)
            estimated_cost_usd = float(local.get("estimated_cost_usd", local.get("estimated_cost", 0.0)))
            if route in MODEL_TIER_ROUTE_MAP.values() and not estimated_cost_usd:
                estimated_cost_usd = self._estimate_cost(model_id)
            return {
                "route": route,
                "model_tier": model_tier,
                "model_id": model_id,
                "model_configured": bool(model_id),
                "confidence": float(local.get("confidence", 0.75)),
                "estimated_cost_usd": estimated_cost_usd,
                "reason": local.get("reason", "Local llamafile route decision."),
                "decision_source": "llamafile",
            }
        return self._deterministic_safety_net(features)

    def estimate_features(
        self,
        *,
        prompt: str,
        security: Dict,
        intent: Dict,
        parsed: Dict,
        complexity: Dict,
        budget: Dict,
        missing_fields: List[str],
        estimated_cost_usd: float,
    ) -> Dict:
        token_count = len(prompt.split())
        api_requirements = []
        lower = prompt.lower()
        if any(term in lower for term in ["weather", "rain", "temperature", "forecast"]):
            api_requirements.append("weather.lookup")
        if any(term in lower for term in ["place", "restaurant", "museum", "near", "visit", "trip", "itinerary", "plan"]):
            api_requirements.append("maps.search_places")
        if any(term in lower for term in ["route", "distance", "transit"]):
            api_requirements.append("maps.route")
        return {
            "prompt": prompt,
            "token_count": token_count,
            "image_present": False,
            "planning_required": intent.get("type") == "travel_planning",
            "reasoning_complexity": "high" if complexity.get("score", 0) >= 60 else "medium" if complexity.get("score", 0) >= 35 else "low",
            "api_requirements": api_requirements,
            "historical_cache_match": 0.0,
            "estimated_output_tokens": 1200 if intent.get("type") == "travel_planning" else 300,
            "budget_remaining": budget.get("remaining_budget_usd", 0.0),
            "budget_mode": budget.get("mode", "healthy"),
            "estimated_cost_usd": estimated_cost_usd,
            "security": security,
            "intent": intent,
            "missing_fields": missing_fields,
            "parsed_summary": {key: value.get("value") for key, value in parsed.items()},
        }

    def _deterministic_safety_net(self, features: Dict) -> Dict:
        if not features["security"].get("safe", True):
            return {
                "route": "BLOCKED",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "confidence": 0.7,
                "estimated_cost_usd": 0.0,
                "reason": "Security scanner blocked prompt before model execution.",
                "decision_source": "deterministic_safety_net",
            }

        intent_type = features["intent"].get("type")
        if intent_type == "booking_request":
            return {
                "route": "OUT_OF_SCOPE",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "confidence": 0.7,
                "estimated_cost_usd": 0.0,
                "reason": "Booking/payment requests are outside Travy planning scope.",
                "decision_source": "deterministic_safety_net",
            }

        if intent_type == "unsupported_live_data":
            return {
                "route": "FALLBACK",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "confidence": 0.72,
                "estimated_cost_usd": 0.0,
                "reason": "Requested live data source is not supported by the planner's factual toolchain.",
                "decision_source": "deterministic_safety_net",
            }

        if intent_type == "budget_math":
            return {
                "route": "LOCAL_LOGIC",
                "model_tier": "local",
                "model_id": settings.LLAMAFILE_MODEL,
                "model_configured": bool(settings.LLAMAFILE_BASE_URL),
                "confidence": 0.75,
                "estimated_cost_usd": 0.0,
                "reason": "Budget calculation is handled by the local control plane.",
                "decision_source": "deterministic_safety_net",
            }

        planning_required = bool(features.get("planning_required"))
        if planning_required:
            budget_mode = features.get("budget_mode", "healthy")
            if budget_mode == "critical":
                return {
                    "route": "API_ONLY_FALLBACK",
                    "model_tier": "none",
                    "model_id": "none",
                    "model_configured": False,
                    "confidence": 0.76,
                    "estimated_cost_usd": 0.0,
                    "reason": "Budget critical: use API-only fallback and avoid Otari planning.",
                    "decision_source": "deterministic_safety_net",
                }

            model_tier, model_id = self._recommended_planner_model(features)
            estimated_cost = self._estimate_cost(model_id)

            if features.get("missing_fields"):
                return {
                    "route": "CLARIFY_REQUIRED",
                    "model_tier": model_tier,
                    "model_id": model_id,
                    "model_configured": bool(model_id),
                    "confidence": 0.73,
                    "estimated_cost_usd": estimated_cost,
                    "reason": f"Required planning fields are missing: {features['missing_fields']}. Local router assigned model for follow-up generation once clarified.",
                    "decision_source": "deterministic_safety_net",
                }

            if estimated_cost > features.get("budget_remaining", 0.0):
                return {
                    "route": "BUDGET_EXCEEDED",
                    "model_tier": "none",
                    "model_id": "none",
                    "model_configured": False,
                    "confidence": 0.75,
                    "estimated_cost_usd": estimated_cost,
                    "reason": "Estimated Otari request cost exceeds remaining budget.",
                    "decision_source": "deterministic_safety_net",
                }

            return {
                "route": MODEL_TIER_ROUTE_MAP.get(model_tier, "COMPRESSED_CHEAP_MODEL"),
                "model_tier": model_tier,
                "model_id": model_id,
                "model_configured": bool(model_id),
                "confidence": 0.78,
                "estimated_cost_usd": estimated_cost,
                "reason": "Local router selected Otari model for final itinerary generation.",
                "decision_source": "deterministic_safety_net",
            }

        if features.get("api_requirements"):
            return {
                "route": "API_ONLY",
                "model_tier": "none",
                "model_id": "none",
                "model_configured": False,
                "confidence": 0.7,
                "estimated_cost_usd": 0.0,
                "reason": "Request can be answered through factual APIs without itinerary generation.",
                "decision_source": "deterministic_safety_net",
            }

        return {
            "route": "LOCAL_MODEL",
            "model_tier": "none",
            "model_id": "none",
            "model_configured": False,
            "confidence": 0.7,
            "estimated_cost_usd": 0.0,
            "reason": "Classification or extraction task handled locally.",
            "decision_source": "deterministic_safety_net",
        }

    def _recommended_planner_model(self, features: Dict) -> tuple[str, str]:
        budget_mode = features.get("budget_mode", "healthy")
        if budget_mode == "low":
            return "cheap", self._get_model_id_for_tier("cheap")

        complexity = features.get("reasoning_complexity")
        if complexity == "high":
            tier = "strong_planner"
        elif complexity == "medium":
            tier = "balanced_planner"
        else:
            tier = "cheap"
        return tier, self._get_model_id_for_tier(tier)

    def _normalize_route(self, selected_route: str, model_tier: str) -> str:
        if selected_route == "OTARI":
            return MODEL_TIER_ROUTE_MAP.get(model_tier, "COMPRESSED_CHEAP_MODEL")
        if selected_route in MODEL_TIER_ROUTE_MAP.values() or selected_route in {
            "API_ONLY", "API_ONLY_FALLBACK", "FALLBACK", "LOCAL_MODEL", "BLOCKED", "CLARIFY_REQUIRED", "BUDGET_EXCEEDED", "OUT_OF_SCOPE"
        }:
            return selected_route
        if selected_route in {"APIONLY", "API_ONLY_FALLBACK"}:
            return "API_ONLY"
        return MODEL_TIER_ROUTE_MAP.get(model_tier, "COMPRESSED_CHEAP_MODEL")

    def _normalize_model_id(self, selected_model_id: Optional[str], model_tier: str) -> str:
        if selected_model_id:
            return selected_model_id
        return self._get_model_id_for_tier(model_tier)

    def _get_model_id_for_tier(self, model_tier: str) -> str:
        if model_tier == "strong_planner":
            return settings.OTARI_STRONG_MODEL
        if model_tier == "balanced_planner":
            return settings.OTARI_BALANCED_MODEL
        if model_tier == "local":
            return settings.OTARI_LOCAL_LLM_MODEL or settings.OTARI_CHEAP_MODEL
        return settings.OTARI_CHEAP_MODEL

    def _estimate_cost(self, model_id: str) -> float:
        if not model_id:
            return 0.0
        client = OtariClient()
        pricing_key = client.get_pricing_key(model_id)
        if not pricing_key:
            return 0.0
        return round(client.calculate_cost(pricing_key, 900, 900), 6)
