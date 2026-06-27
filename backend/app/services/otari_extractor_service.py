import json
import logging
from app.services.otari_client import OtariClient
from app.core.config import settings

logger = logging.getLogger("travy.otari_extractor_service")

class OtariExtractorService:
    async def extract(self, prompt: str) -> dict:
        system_prompt = (
            "You are Travy, a cost-aware travel planning AI assistant built on the Mozilla.ai Otari gateway.\n\n"
            "You operate inside a multi-stage pipeline. Your ONLY jobs are:\n"
            "1. Extract structured travel constraints from natural-language input\n"
            "2. Generate human-readable itinerary explanations from pre-ranked place data\n"
            "3. Summarize why each stop was selected (referencing real fit scores)\n\n"
            "You NEVER invent locations, coordinates, prices, opening hours, ratings, or travel times.\n"
            "All place data is provided to you by the backend. You explain and narrate — you do not create facts.\n\n"
            "────────────────────────────────────────\n"
            "RESPONSE CONTRACT — STRICT JSON ONLY\n"
            "────────────────────────────────────────\n\n"
            "For CONSTRAINT EXTRACTION tasks, respond ONLY with this JSON (no preamble, no markdown):\n"
            "{\n"
            "  \"task\": \"extract_constraints\",\n"
            "  \"city\": \"<string | null>\",\n"
            "  \"group_size\": <integer | null>,\n"
            "  \"budget_per_person_inr\": <integer | null>,\n"
            "  \"start_time\": \"<HH:MM | null>\",\n"
            "  \"end_time\": \"<HH:MM | null>\",\n"
            "  \"moods\": [\"<shopping|food|photos|culture|adventure|relaxation|nightlife|...>\"],\n"
            "  \"energy\": \"<low|medium|high | null>\",\n"
            "  \"transport\": \"<walking|auto|cab|metro | null>\",\n"
            "  \"dietary\": \"<string | null>\",\n"
            "  \"crowd_tolerance\": \"<low|medium|high | null>\",\n"
            "  \"confidence\": <0.0–1.0>,\n"
            "  \"gaps\": [\"<list of missing fields the user did not specify>\"]\n"
            "}"
        )
        
        user_prompt = (
            "TASK: extract_constraints\n\n"
            f"USER INPUT:\n\"{prompt}\"\n\n"
            "Extract all travel constraints from the above input.\n"
            "Return JSON matching the extract_constraints schema exactly.\n"
            "Do not add any fields not in the schema.\n"
            "Do not include any text outside the JSON object."
        )
        
        client = OtariClient()
        try:
            res = await client.generate_completion(
                model=settings.OTARI_CHEAP_MODEL,
                prompt=f"{system_prompt}\n\n{user_prompt}",
                max_tokens=300
            )
            
            # Check if guardrail blocked it
            if res.get("blocked"):
                return {
                    "extracted": {},
                    "used_otari": True,
                    "success": False,
                    "error": "prompt_injection_detected"
                }
                
            text = res.get("response_preview", "").strip()
            
            # Clean markdown code fences if present
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[0].startswith("```json"):
                    text = "\n".join(lines[1:-1])
                elif lines[0].startswith("```"):
                    text = "\n".join(lines[1:-1])
            
            data = json.loads(text.strip())
            
            # Translate task key or format constraints structure
            extracted_data = {
                "city": data.get("city"),
                "group_size": data.get("group_size"),
                "budget_per_person_inr": data.get("budget_per_person_inr"),
                "start_time": data.get("start_time"),
                "end_time": data.get("end_time"),
                "moods": data.get("moods") or [],
                "energy": data.get("energy"),
                "transport": data.get("transport"),
                "dietary_restrictions": data.get("dietary"), # keep key mapping compatible
                "crowd_tolerance": data.get("crowd_tolerance"),
                "gaps": data.get("gaps") or []
            }
            
            return {
                "extracted": extracted_data,
                "used_otari": True,
                "success": True
            }
        except Exception as e:
            logger.warning(f"Otari constraints extraction failed: {e}")
            return {
                "extracted": {},
                "used_otari": True,
                "success": False,
                "error": str(e)
            }
