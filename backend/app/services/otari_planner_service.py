import json
import logging
from typing import Dict, Any, List, Optional
from app.integrations.otari_client import OtariClient
from app.core.config import settings

logger = logging.getLogger("travy.otari_planner_service")

class OtariPlannerService:
    def __init__(self):
        self.otari_client = OtariClient()

    async def generate_itinerary(
        self,
        model_tier: str,
        constraints: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        request_id: Optional[str] = None,
        session_id: str = "demo"
    ) -> Dict[str, Any]:
        # Map model tier to configured model key
        if model_tier == "strong_planner":
            model_id = settings.OTARI_STRONG_MODEL
        elif model_tier == "balanced_planner":
            model_id = settings.OTARI_BALANCED_MODEL
        elif model_tier == "cheap":
            model_id = settings.OTARI_CHEAP_MODEL
        else:
            model_id = settings.OTARI_STRONG_MODEL
            
        system_prompt = (
            "You are Travy's Smart Itinerary Planner. Your task is to output a single JSON object. "
            "Do NOT include any conversational text or markdown code blocks outside the JSON.\n\n"
            "CRITICAL RULES:\n"
            "1. You must ONLY select stops from the candidate places list provided. DO NOT invent new place names, addresses, or IDs.\n"
            "2. Each selected stop in your 'stops' list must contain the exact 'place_id' and 'name' from the candidate list.\n"
            "3. The stops must fit within the specified time window (start_time to end_time) and budget per person.\n"
            "4. Format the output precisely in JSON matching the following schema:\n"
            "{\n"
            "  \"title\": \"String itinerary title\",\n"
            "  \"summary\": \"Short summary of the plan\",\n"
            "  \"stops\": [\n"
            "    {\n"
            "      \"place_id\": \"matching candidate place id\",\n"
            "      \"name\": \"exact candidate name\",\n"
            "      \"category\": \"candidate category\",\n"
            "      \"start_time\": \"e.g. 2:00 PM\",\n"
            "      \"end_time\": \"e.g. 3:30 PM\",\n"
            "      \"estimated_cost_per_person_inr\": 250,\n"
            "      \"why_selected\": [\"reason 1\", \"reason 2\"]\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        # Serialize candidates for the prompt
        candidates_str = json.dumps([
            {
                "id": c["id"],
                "name": c["name"],
                "category": c["category"],
                "score": c.get("total_score", 0),
                "estimated_cost_inr": c.get("estimated_cost_inr", 100),
                "address": c.get("address", "")
            }
            for c in candidates
        ], indent=2)
        
        prompt = (
            f"{system_prompt}\n\n"
            f"--- CONSTRAINTS ---\n"
            f"City: {constraints.get('city')}\n"
            f"Group Size: {constraints.get('group_size')}\n"
            f"Budget/person: ₹{constraints.get('budget_per_person_inr')}\n"
            f"Time window: {constraints.get('start_time')} to {constraints.get('end_time')}\n"
            f"Moods: {', '.join(constraints.get('moods', []))}\n"
            f"Energy/Comfort preference: {constraints.get('energy')}\n\n"
            f"--- CANDIDATE PLACES ---\n"
            f"{candidates_str}\n\n"
            f"Output the JSON object now:"
        )
        
        res = await self.otari_client.generate_completion(
            model=model_id,
            prompt=prompt,
            max_tokens=1000,
            request_id=request_id,
            session_id=session_id
        )
        
        text = res.get("response_preview", "").strip()
        
        # Strip markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```json"):
                text = "\n".join(lines[1:-1])
            elif lines[0].startswith("```"):
                text = "\n".join(lines[1:-1])
                
        # Parse JSON
        itinerary_data = json.loads(text.strip())
        
        # Attach execution evidence metadata
        itinerary_data["_otari_evidence"] = {
            "model_id": model_id,
            "latency_ms": res.get("latency_ms", 0),
            "cost_usd": res.get("cost_usd", 0.0),
            "input_tokens": res.get("input_tokens", 0),
            "output_tokens": res.get("output_tokens", 0)
        }
        
        return itinerary_data

    async def attempt_repair(
        self,
        error_message: str,
        original_output: str,
        constraints: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        request_id: Optional[str] = None,
        session_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Calls a cheaper model once to repair invalid JSON or schema violations.
        """
        logger.info(f"Attempting repair for itinerary generation error: {error_message}")
        model_id = settings.OTARI_CHEAP_MODEL
        
        prompt = (
            f"You are a JSON repair assistant. The following output failed validation:\n"
            f"```json\n{original_output}\n```\n"
            f"Validation Error: {error_message}\n\n"
            f"Make sure to output a single, syntactically correct JSON object matching the required schema.\n"
            f"Ensure all place_ids are selected strictly from the candidates:\n"
            f"{[c['id'] for c in candidates]}\n\n"
            f"Output repaired JSON now:"
        )
        
        res = await self.otari_client.generate_completion(
            model=model_id,
            prompt=prompt,
            max_tokens=800,
            request_id=request_id,
            session_id=session_id
        )
        
        text = res.get("response_preview", "").strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```json"):
                text = "\n".join(lines[1:-1])
            elif lines[0].startswith("```"):
                text = "\n".join(lines[1:-1])
                
        itinerary_data = json.loads(text.strip())
        itinerary_data["_otari_evidence"] = {
            "model_id": model_id,
            "latency_ms": res.get("latency_ms", 0),
            "cost_usd": res.get("cost_usd", 0.0),
            "input_tokens": res.get("input_tokens", 0),
            "output_tokens": res.get("output_tokens", 0),
            "repaired": True
        }
        return itinerary_data
