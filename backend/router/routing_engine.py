from schemas import LlamafileOutput


class RoutingEngine:
    def select_model(self, llama: LlamafileOutput, category: str) -> tuple[str, str]:
        if category == "VISION":
            return "otari-vision", "Vision task routed to otari-vision"

        if llama.complexity_score < 25:
            return "otari-small", "Complexity below 25, routed to otari-small"
        if llama.complexity_score <= 60:
            return "otari-medium", "Complexity between 25-60, routed to otari-medium"
        return "otari-large", "Complexity above 60, routed to otari-large"
