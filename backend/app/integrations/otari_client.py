import json
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
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
        # Inject user message list matching exact payload shape
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1, # Consistent low temperature from rules
            "guardrails": [
                {"profile": "prompt-injection", "mode": "block"}
            ]
        }
        
        # We handle guardrail block status_code 400 at this client layer
        start_time = time.perf_counter()
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.OTARI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                
                if response.status_code == 400:
                    body = response.json()
                    guardrail_header = response.headers.get("X-Otari-Guardrails", "")
                    
                    PersistenceService.save_api_call_log(
                        log_id=f"api_call_block_{os.urandom(4).hex()}",
                        request_id=request_id or "system",
                        provider="otari",
                        endpoint_name="chat/completions",
                        status="400",
                        latency_ms=latency_ms,
                        error_message="Guardrail Blocked Request",
                        cost_usd=0.0
                    )
                    
                    return {
                        "blocked": True,
                        "reason": body.get("message", "guardrail_block"),
                        "guardrail_header": guardrail_header,
                        "response_preview": '{"task": "blocked", "reason": "prompt_injection_detected"}'
                    }
                
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                PersistenceService.save_api_call_log(
                    log_id=f"api_call_err_{os.urandom(4).hex()}",
                    request_id=request_id or "system",
                    provider="otari",
                    endpoint_name="chat/completions",
                    status="ERROR",
                    latency_ms=int((time.perf_counter() - start_time) * 1000),
                    error_message=str(e),
                    cost_usd=0.0
                )
                raise
                
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices returned from Otari API.")
            
        content = choices[0].get("message", {}).get("content", "")
        
        # Token usage extraction
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        
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
            estimated_cost_usd=actual_cost,
            actual_cost_usd=actual_cost,
            usage_source="otari_response",
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        # Save normal trace log
        PersistenceService.save_api_call_log(
            log_id=f"api_call_{uuid.uuid4().hex[:8]}",
            request_id=request_id or "system",
            provider="otari",
            endpoint_name="chat/completions",
            status="200",
            latency_ms=latency_ms,
            error_message="",
            cost_usd=actual_cost
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
