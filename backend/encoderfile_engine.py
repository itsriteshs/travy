import hashlib
import re

from schemas import EncoderfileOutput


class EncoderfileEngine:
    """Local semantic layer inspired by Encoderfile."""

    def analyze(self, prompt: str) -> EncoderfileOutput:
        text = prompt.lower()
        tokens = re.findall(r"\w+", text)
        length = len(tokens)

        category = "SIMPLE"
        if any(word in text for word in ["image", "photo", "vision"]):
            category = "VISION"
        elif length > 80 or any(word in text for word in ["optimize", "constraints", "multi-city", "group"]):
            category = "COMPLEX"
        elif length > 35:
            category = "MEDIUM"

        intent = "travel_planning"
        if not any(word in text for word in ["travel", "trip", "itinerary", "hangout", "visit", "tour"]):
            intent = "general_query"

        embedding_id = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
        # Deterministic cache flag for repeatable routing decisions.
        cache_hit = int(embedding_id[-1], 16) % 4 == 0

        return EncoderfileOutput(
            intent=intent,
            category=category,
            cache_hit=cache_hit,
            embedding_id=embedding_id,
        )
