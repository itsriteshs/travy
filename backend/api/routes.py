from fastapi import APIRouter
import httpx
import base64
import json
import asyncio
import websockets
from urllib.parse import urlencode
from pydantic import BaseModel

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


class TranscribeRequest(BaseModel):
    audio_base64: str


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


@router.post("/transcribe")
async def transcribe(payload: TranscribeRequest) -> dict:
    """Transcribe audio using Smallest.ai Pulse speech-to-text API via WebSocket."""
    if not settings.smallest_ai_api_key:
        return {"error": "Smallest.ai API key not configured", "text": "", "status": "error"}

    try:
        # Decode base64 audio to binary PCM data
        # Frontend now sends raw PCM16 at 16000 Hz (already resampled and encoded)
        audio_data = base64.b64decode(payload.audio_base64)
        print(f"[TRANSCRIBE] Received PCM data: {len(audio_data)} bytes")
        
        if len(audio_data) == 0:
            return {"error": "Audio data is empty", "text": "", "status": "error"}
        
        # WebSocket URL with audio configuration parameters
        params = {
            "language": "en",
            "encoding": "linear16",
            "sample_rate": "16000",
            "word_timestamps": "false"
        }
        ws_url = f"wss://api.smallest.ai/waves/v1/pulse/get_text?{urlencode(params)}"
        print(f"[TRANSCRIBE] Connecting to: {ws_url}")
        
        headers = {"Authorization": f"Bearer {settings.smallest_ai_api_key}"}
        
        transcript = ""
        
        async with websockets.connect(ws_url, additional_headers=headers) as ws:
            print("[TRANSCRIBE] WebSocket connected, sending audio...")
            
            # Send audio in chunks
            chunk_size = 4096
            chunks_sent = 0
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                await ws.send(chunk)
                chunks_sent += 1
            print(f"[TRANSCRIBE] Sent {chunks_sent} chunks ({len(audio_data)} bytes total)")
            
            # Signal end of audio
            finalize_msg = json.dumps({"type": "finalize"})
            await ws.send(finalize_msg)
            print(f"[TRANSCRIBE] Sent finalize signal")
            
            # Collect responses
            print("[TRANSCRIBE] Waiting for transcription...")
            async for message in ws:
                try:
                    data = json.loads(message)
                    print(f"[TRANSCRIBE] Received: {data}")
                    
                    if data.get("is_final"):
                        transcript = data.get("transcript", "")
                        print(f"[TRANSCRIBE] ✓ Final transcript: '{transcript}'")
                        break
                    else:
                        # Use partial result
                        partial = data.get("transcript", "")
                        if partial:
                            transcript = partial
                            print(f"[TRANSCRIBE] Partial: '{partial}'")
                except json.JSONDecodeError:
                    print(f"[TRANSCRIBE] Non-JSON message received")
        
        print(f"[TRANSCRIBE] Final result: '{transcript}'")
        return {
            "text": transcript,
            "status": "success",
        }
    except Exception as e:
        print(f"[TRANSCRIBE] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "text": "", "status": "error"}


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
