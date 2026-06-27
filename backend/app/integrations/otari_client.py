import json
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any
from app.integrations.base_client import BaseClient
from app.core.config import settings
from app.services.persistence_service import PersistenceService

class OtariClient(BaseClient):
    def __init__(self):
        super().__init__(provider_name="otari", base_url=settings.OTARI_BASE_URL)
        self.api_key = settings.OTARI_API_KEY
        self.pricing_data = self._load_pricing()

    def _load_pricing(self) -> dict:
        base_dir = Path(__file__).resolve().parents[3]
        pricing_path = base_dir / "config" / "model-pricing.json"
        if pricing_path.exists():
            with open(pricing_path, "r") as f:
                return json.load(f)
        return {}

    def get_pricing_key(self, model: str) -> Optional[str]:
        model_lower = model.lower()
        if ":" in model_lower:
            _, model_name = model_lower.split(":", 1)
        else:
            model_name = model_lower
            
        for key in self.pricing_data.keys():
            if key in model_name or model_name in key:
                return key
                
        # Fallback mappings
        if "gemma" in model_lower:
            return "gemma-3-27b-it"
        elif "qwen" in model_lower:
            return "qwen-2.5-32b"
        elif "llama" in model_lower:
            return "llama-3.3-70b"
        return None

    def calculate_cost(self, model_key: Optional[str], input_tokens: int, output_tokens: int) -> float:
        if not model_key or model_key not in self.pricing_data:
            return 0.0
        pricing = self.pricing_data[model_key]
        in_price = pricing.get("input_token_price", 0.0)
        out_price = pricing.get("output_token_price", 0.0)
        return (input_tokens * in_price) + (output_tokens * out_price)

    async def generate_completion(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 500,
        request_id: Optional[str] = None,
        session_id: str = "demo"
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.0
        }
        
        # Make the request through base client
        result = await self.request(
            method="POST",
            path="chat/completions",
            request_id=request_id,
            headers=headers,
            json_data=payload
        )
        
        data = result["data"]
        latency_ms = result["latency_ms"]
        
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices returned from Otari API.")
            
        content = choices[0].get("message", {}).get("content", "")
        
        # Token usage extraction
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        
        # Fallback local estimation if usage is not provided by the API
        if input_tokens is None:
            input_tokens = int(len(prompt.split()) * 1.3)
        if output_tokens is None:
            output_tokens = int(len(content.split()) * 1.3)
            
        pricing_key = self.get_pricing_key(model)
        actual_cost = self.calculate_cost(pricing_key, input_tokens, output_tokens)
        
        # Store entry in budget ledger
        import uuid
        ledger_id = f"ledg_{uuid.uuid4().hex[:8]}"
        PersistenceService.save_budget_ledger(
            ledger_id=ledger_id,
            session_id=session_id,
            request_id=request_id or "system",
            provider="otari",
            model_id=model,
            estimated_cost_usd=actual_cost, # We record actual cost or estimates
            actual_cost_usd=actual_cost,
            usage_source="otari_response",
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        return {
            "backend": True,
            "otari_reachable": True,
            "model": model,
            "latency_ms": latency_ms,
            "response_preview": content.strip(),
            "mode": "live",
            "cost_usd": actual_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
