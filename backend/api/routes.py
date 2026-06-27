from fastapi import APIRouter

from agents.budget_agent import BudgetAgent
from agents.router_agent import RouterAgent
from agents.security_agent import SecurityAgent
from budget.budget_manager import BudgetManager
from config import settings
from encoderfile_engine import EncoderfileEngine
from otari.client import generate_itinerary
from schemas import BudgetStatus, ChatRequest, ChatResponse, TransparencyPanel
from security.llamafile_engine import LlamafileEngine
from tools.mcpd_tools import budget_tool, maps_tool, places_tool, weather_tool


router = APIRouter()

encoder = EncoderfileEngine()
llamafile = LlamafileEngine()
security_agent = SecurityAgent()
budget_manager = BudgetManager(initial_budget=settings.initial_budget_usd)
budget_agent = BudgetAgent(manager=budget_manager)
router_agent = RouterAgent()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/budget")
async def budget() -> dict:
    return {
        "total_budget": settings.initial_budget_usd,
        "current_spend": budget_manager.total_spend(),
        "total_spend": budget_manager.total_spend(),
        "remaining_budget": budget_manager.remaining(),
    }


@router.get("/provider-check")
async def provider_check() -> dict:
    return {
        "otari_base_url": settings.otari_base_url,
        "has_api_key": bool(settings.otari_api_key),
        "models": {
            "otari-small": settings.otari_small_model,
            "otari-medium": settings.otari_medium_model,
            "otari-large": settings.otari_large_model,
            "otari-vision": settings.otari_vision_model,
        },
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    prompt = payload.prompt.strip()

    # Required flow: encoder embeddings + intent/category.
    encoder_out = encoder.analyze(prompt)

    # Required flow: local security + complexity + cost analysis.
    llama_out = llamafile.analyze(prompt, encoder_out.category)

    allowed, security_message = security_agent.evaluate(llama_out)
    if not allowed:
        transparency = TransparencyPanel(
            selected_model="none",
            complexity_score=llama_out.complexity_score,
            routing_reason=security_message,
            estimated_cost=0,
            remaining_budget=budget_manager.remaining(),
            security_status=llama_out.security_status,
            risk_score=llama_out.risk_score,
            intent=encoder_out.intent,
            category=encoder_out.category,
            cache_hit=encoder_out.cache_hit,
        )
        budget_status = BudgetStatus(
            total_budget=settings.initial_budget_usd,
            current_request_cost=0,
            total_spend=budget_manager.total_spend(),
            remaining_budget=budget_manager.remaining(),
            downgraded=False,
            exhausted=budget_manager.remaining() <= 0,
        )
        return ChatResponse(response="Request blocked for safety reasons.", transparency=transparency, budget=budget_status)

    # Required flow: dynamic model selection.
    selected_model, routing_reason = router_agent.finalize(encoder_out, llama_out)

    # Required flow: budget validation and model downgrade if needed.
    final_model, final_cost, downgraded, exhausted = budget_agent.validate(
        llama_out.estimated_cost, selected_model
    )

    if exhausted and final_cost == 0:
        response_text = "AI budget exhausted.\nSwitching to lightweight mode."
    else:
        city = "destination"
        if " in " in prompt.lower():
            city = prompt.split(" in ", 1)[1].split(" for ", 1)[0].strip()

        mcpd_context = {
            "weather": weather_tool(city),
            "places": places_tool(city),
            "map": maps_tool(city),
            "budget": budget_tool("USD"),
        }

        response_text = await generate_itinerary(prompt=prompt, model=final_model, mcpd_context=mcpd_context)
        if exhausted:
            response_text += "\n\nAI budget exhausted.\nSwitching to lightweight mode."

    transparency = TransparencyPanel(
        selected_model=final_model,
        complexity_score=llama_out.complexity_score,
        routing_reason=routing_reason if not downgraded else f"{routing_reason}. Downgraded due to budget.",
        estimated_cost=final_cost,
        remaining_budget=budget_manager.remaining(),
        security_status=llama_out.security_status,
        risk_score=llama_out.risk_score,
        intent=encoder_out.intent,
        category=encoder_out.category,
        cache_hit=encoder_out.cache_hit,
    )

    budget_status = BudgetStatus(
        total_budget=settings.initial_budget_usd,
        current_request_cost=final_cost,
        total_spend=budget_manager.total_spend(),
        remaining_budget=budget_manager.remaining(),
        downgraded=downgraded,
        exhausted=exhausted,
    )

    return ChatResponse(response=response_text, transparency=transparency, budget=budget_status)
