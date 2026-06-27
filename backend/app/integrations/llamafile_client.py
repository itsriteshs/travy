import json
import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("travy.llamafile_client")


class LlamafileClient:
    """OpenAI-compatible client for local-only control-plane decisions."""

    def __init__(self):
        self.base_url = settings.LLAMAFILE_BASE_URL.rstrip("/")
        self.model = settings.LLAMAFILE_MODEL
        self.enabled = bool(self.base_url)

    async def structured_json(
        self,
        *,
        system_prompt: str,
        user_payload: Dict[str, Any],
        timeout: float = 60.0,
    ) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=True)},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload)
                response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:
            logger.warning("Local llamafile structured call failed: %s", exc)
            return None
