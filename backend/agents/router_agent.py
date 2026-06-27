from router.routing_engine import RoutingEngine
from schemas import EncoderfileOutput, LlamafileOutput


class RouterAgent:
    def __init__(self) -> None:
        self.engine = RoutingEngine()

    def finalize(self, encoder: EncoderfileOutput, llama: LlamafileOutput) -> tuple[str, str]:
        return self.engine.select_model(llama, encoder.category)
