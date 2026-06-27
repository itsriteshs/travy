from schemas import LlamafileOutput


class SecurityAgent:
    def evaluate(self, llama: LlamafileOutput) -> tuple[bool, str]:
        if llama.security_status == "BLOCKED":
            return False, "Request blocked due to prompt injection/jailbreak risk."
        return True, "Security checks passed."
