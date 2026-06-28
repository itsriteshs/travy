from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


class EncoderfileOutput(BaseModel):
    intent: str
    category: str
    cache_hit: bool
    embedding_id: str


class LlamafileOutput(BaseModel):
    security_status: str
    risk_score: int
    complexity_score: int
    estimated_tokens: int
    estimated_cost: float
    selected_model: str
    routing_reason: str


class BudgetStatus(BaseModel):
    total_budget: float
    current_request_cost: float
    total_spend: float
    remaining_budget: float
    downgraded: bool
    exhausted: bool


class TransparencyPanel(BaseModel):
    selected_model: str
    complexity_score: int
    routing_reason: str
    estimated_cost: float
    remaining_budget: float
    security_status: str
    risk_score: int
    intent: str
    category: str
    cache_hit: bool


class ChatResponse(BaseModel):
    response: str
    transparency: TransparencyPanel
    budget: BudgetStatus


class TravisonVisionSummary(BaseModel):
    primary_subject: str
    landmarks: list[str]
    labels: list[str]


class TravisonResponse(BaseModel):
    vision: TravisonVisionSummary
    prompt_used: str
    result: ChatResponse
