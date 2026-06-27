import re

from schemas import LlamafileOutput


class LlamafileEngine:
    """Local runtime reasoning + safety checker inspired by Llamafile responsibilities."""

    _blocked_patterns = [
        r"ignore\s+previous\s+instructions",
        r"reveal\s+system\s+prompt",
        r"developer\s+mode",
        r"jailbreak",
        r"api\s*key",
        r"role\s*hijack",
    ]

    _suspicious_patterns = [
        r"bypass",
        r"override",
        r"do\s+anything\s+now",
        r"hidden\s+instructions",
    ]

    def analyze(self, prompt: str, category: str) -> LlamafileOutput:
        text = prompt.lower()
        words = re.findall(r"\w+", text)

        risk_score = 1
        security_status = "SAFE"

        if any(re.search(p, text) for p in self._blocked_patterns):
            risk_score = 95
            security_status = "BLOCKED"
        elif any(re.search(p, text) for p in self._suspicious_patterns):
            risk_score = 55
            security_status = "SUSPICIOUS"

        complexity_score = min(100, max(5, len(words) + (15 if category == "COMPLEX" else 0)))
        if category == "VISION":
            complexity_score = max(complexity_score, 70)

        estimated_tokens = int(len(prompt) * 0.45) + 120
        if complexity_score < 25:
            base_model = "otari-small"
            multiplier = 0.0000018
            reason = "Low constraint travel request"
        elif complexity_score <= 60:
            base_model = "otari-medium"
            multiplier = 0.0000032
            reason = "Medium complexity travel itinerary generation"
        else:
            base_model = "otari-large"
            multiplier = 0.0000052
            reason = "Multi-constraint group itinerary generation"

        if category == "VISION":
            base_model = "otari-vision"
            multiplier = 0.000006
            reason = "Vision-enabled travel planning request"

        estimated_cost = round(estimated_tokens * multiplier, 6)

        return LlamafileOutput(
            security_status=security_status,
            risk_score=risk_score,
            complexity_score=complexity_score,
            estimated_tokens=estimated_tokens,
            estimated_cost=estimated_cost,
            selected_model=base_model,
            routing_reason=reason,
        )
