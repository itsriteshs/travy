class InjectionService:
    def scan(self, prompt: str) -> dict:
        suspicious = [
            "ignore previous instructions",
            "reveal api key",
            "system prompt",
            "developer message",
            "bypass rules",
            "act as",
            "forget your instructions"
        ]
        prompt_lower = prompt.lower()
        detected = [p for p in suspicious if p in prompt_lower]
        safe = len(detected) == 0
        risk_score = 90 if not safe else 0
        
        return {
            "safe": safe,
            "risk_score": risk_score,
            "detected": detected,
            "action": "blocked" if not safe else "allowed",
            "model_call_allowed": safe
        }
