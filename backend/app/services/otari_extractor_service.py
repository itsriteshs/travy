import json
from app.services.otari_client import OtariClient
from app.core.config import settings

class OtariExtractorService:
    async def extract(self, prompt: str) -> dict:
        system_prompt = (
            "You are a travel request parameter extractor. Your task is to output a single JSON object. "
            "Do NOT include conversational text or markdown formatting outside the JSON. "
            "Fields: "
            "city (string or null), group_size (integer or null), "
            "budget_per_person_inr (integer or null), start_time (string or null), "
            "end_time (string or null), moods (array of strings), energy (string, e.g. medium-low, medium, high), "
            "transport (string or null), crowd_tolerance (string or null)."
        )
        
        client = OtariClient()
        try:
            res = await client.generate_completion(
                model=settings.OTARI_CHEAP_MODEL,
                prompt=f"{system_prompt}\n\nExtract from this prompt:\n\"{prompt}\"\n\nJSON output:",
                max_tokens=200
            )
            text = res.get("response_preview", "").strip()
            
            # Clean markdown code fences if present
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[0].startswith("```json"):
                    text = "\n".join(lines[1:-1])
                elif lines[0].startswith("```"):
                    text = "\n".join(lines[1:-1])
            
            data = json.loads(text.strip())
            return {
                "extracted": data,
                "used_otari": True,
                "success": True
            }
        except Exception as e:
            return {
                "extracted": {},
                "used_otari": True,
                "success": False,
                "error": str(e)
            }
        
