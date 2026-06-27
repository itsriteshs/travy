import re

INJECTION_WEIGHTS = {
    "role_escalation":      30,   # "you are now", "act as", "pretend to be"
    "instruction_override": 25,   # "ignore previous", "forget your", "disregard"
    "prompt_extraction":    25,   # "reveal your", "show me your prompt", "system message"
    "jailbreak_pattern":    20,   # "DAN mode", "developer mode", "no restrictions"
}

INJECTION_PATTERNS = {
    "role_escalation":      [r"you are now", r"\bact as\b", r"pretend to be", r"roleplay as"],
    "instruction_override": [r"ignore (previous|above|all|your|instructions)", r"forget (your|all|rules)", r"disregard"],
    "prompt_extraction":    [r"reveal your", r"show me your (prompt|instructions)", r"system (message|prompt)"],
    "jailbreak_pattern":    [r"DAN mode", r"developer mode", r"no restrictions", r"jailbreak", r"api key", r"reveal.*key", r"system prompt"],
}

class InjectionService:
    def scan(self, text: str) -> dict:
        risk_score = 0
        matched = []
        for category, patterns in INJECTION_PATTERNS.items():
            for p in patterns:
                if re.search(p, text, re.IGNORECASE):
                    risk_score += INJECTION_WEIGHTS[category]
                    matched.append({"category": category, "pattern": p})
                    break  # only count each category once
        blocked = risk_score >= 70
        return {
            "safe": not blocked,
            "risk_score": min(risk_score, 100),
            "detected": [m["pattern"] for m in matched],
            "action": "blocked" if blocked else "allowed",
            "model_call_allowed": not blocked,
            "matched_patterns": matched
        }
