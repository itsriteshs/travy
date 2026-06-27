import time
import httpx
from app.core.config import settings

class OtariClient:
    def __init__(self):
        self.base_url = settings.OTARI_BASE_URL.rstrip("/")
        self.api_key = settings.OTARI_API_KEY
        self.mode = settings.OTARI_MODE

    async def generate_completion(self, model: str, prompt: str, max_tokens: int = 5) -> dict:
        """
        Sends an async POST request to the Otari chat completions API.
        """
        url = f"{self.base_url}/chat/completions"
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
        
        start_time = time.perf_counter()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=15.0)
            response.raise_for_status()
            
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        data = response.json()
        
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices returned from Otari API.")
            
        content = choices[0].get("message", {}).get("content", "")
        
        return {
            "backend": True,
            "otari_reachable": True,
            "model": model,
            "latency_ms": latency_ms,
            "response_preview": content.strip(),
            "mode": "live"
        }
