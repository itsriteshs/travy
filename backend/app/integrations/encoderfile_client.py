import logging
from typing import List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("travy.encoderfile_client")


class EncoderfileClient:
    """HTTP client for local encoderfile embeddings and similarity checks."""

    def __init__(self):
        self.base_url = settings.ENCODERFILE_BASE_URL.rstrip("/")
        self.enabled = bool(self.base_url)

    async def embed(self, texts: List[str], normalize: bool = True) -> Optional[List[List[float]]]:
        if not self.enabled:
            return None
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/predict",
                    json={"inputs": texts, "normalize": normalize},
                )
                response.raise_for_status()
            embeddings = []
            for item in response.json().get("results", []):
                if isinstance(item, dict) and "embedding" in item:
                    embeddings.append(item["embedding"])
                elif isinstance(item, dict) and "embeddings" in item:
                    vectors = item["embeddings"]
                    embeddings.append(vectors[0] if vectors else [])
                elif isinstance(item, list):
                    embeddings.append(item)
            return embeddings
        except Exception as exc:
            logger.warning("Encoderfile embedding call failed: %s", exc)
            return None


def cosine_similarity(left: List[float], right: List[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
