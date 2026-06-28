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

    _constraint_keywords = [
        "budget",
        "cheap",
        "luxury",
        "family",
        "kids",
        "elderly",
        "wheelchair",
        "vegetarian",
        "vegan",
        "rain",
        "weather",
        "safety",
        "time",
        "start",
        "end",
        "morning",
        "night",
        "avoid",
        "must",
        "prefer",
    ]

    _logistics_keywords = [
        "route",
        "distance",
        "transport",
        "metro",
        "taxi",
        "flight",
        "train",
        "hotel",
        "check-in",
        "check out",
        "pickup",
        "drop",
        "multi-city",
        "across",
    ]

    def _extract_trip_days(self, text: str) -> int:
        max_days = 0
        for value, unit in re.findall(r"(\d+)\s*(day|days|week|weeks)", text):
            count = int(value)
            if "week" in unit:
                count *= 7
            max_days = max(max_days, count)
        return max_days

    def _extract_group_size(self, text: str) -> int:
        m = re.search(r"(\d+)\s*(friends?|people|persons?|travellers?|travelers?|pax)", text)
        if not m:
            return 1
        return max(1, int(m.group(1)))

    def _semantic_complexity(self, text: str, category: str, words: list[str]) -> int:
        score = 12

        trip_days = self._extract_trip_days(text)
        if trip_days:
            score += min(trip_days * 5, 45)
            if trip_days >= 7:
                score += 12

        group_size = self._extract_group_size(text)
        if group_size >= 5:
            score += 10
        if group_size >= 9:
            score += 8

        if any(k in text for k in ["multi-city", "across", "city to city", "multiple cities"]):
            score += 18

        constraints_hit = sum(1 for k in self._constraint_keywords if k in text)
        logistics_hit = sum(1 for k in self._logistics_keywords if k in text)
        score += min(constraints_hit * 3, 18)
        score += min(logistics_hit * 4, 20)

        # Keep length as a weak signal only.
        score += min(len(words) // 18, 10)

        if category == "COMPLEX":
            score += 10
        elif category == "MEDIUM":
            score += 4

        return max(5, min(100, score))

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

        complexity_score = self._semantic_complexity(text, category, words)
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
