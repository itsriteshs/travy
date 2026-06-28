from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import httpx
import base64
import json
import asyncio
import re
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
from schemas import (
    BudgetStatus,
    ChatRequest,
    ChatResponse,
    TransparencyPanel,
    TravisonResponse,
    TravisonVisionSummary,
)
from security.llamafile_engine import LlamafileEngine
from tools.mcpd_tools import budget_tool, maps_tool, places_tool, weather_tool


class TranscribeRequest(BaseModel):
    audio_base64: str


def _merge_transcript_chunks(current: str, incoming: str) -> str:
    current = (current or "").strip()
    incoming = (incoming or "").strip()

    if not incoming:
        return current
    if not current:
        return incoming

    # If one chunk fully contains the other, keep the longer hypothesis.
    if incoming in current:
        return current
    if current in incoming:
        return incoming

    # If the new chunk starts with current text, it is likely an extended hypothesis.
    if incoming.startswith(current):
        return incoming

    # If current already starts with incoming, keep current.
    if current.startswith(incoming):
        return current

    # Stitch chunks using maximal suffix/prefix overlap.
    max_overlap = min(len(current), len(incoming), 240)
    for overlap in range(max_overlap, 0, -1):
        if current.endswith(incoming[:overlap]):
            return f"{current}{incoming[overlap:]}".strip()

    return f"{current} {incoming}".strip()


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
        "has_gemini_key": bool(settings.gemini_api_key),
        "models": {
            "otari-small": settings.otari_small_model,
            "otari-medium": settings.otari_medium_model,
            "otari-large": settings.otari_large_model,
            "otari-vision": settings.otari_vision_model,
            "gemini-vision": settings.gemini_vision_model,
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
        saw_final = False
        
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
            
            # Collect responses. Some providers can emit multiple final chunks,
            # so we keep listening briefly after the first final signal.
            print("[TRANSCRIBE] Waiting for transcription...")
            while True:
                timeout_seconds = 1.8 if saw_final else 6.0
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=timeout_seconds)
                except asyncio.TimeoutError:
                    break

                try:
                    data = json.loads(message)
                    print(f"[TRANSCRIBE] Received: {data}")

                    text = str(data.get("transcript", "")).strip()
                    if text:
                        transcript = _merge_transcript_chunks(transcript, text)

                    if data.get("is_final"):
                        saw_final = True

                    message_type = str(data.get("type", "")).lower()
                    if message_type in {"done", "completed", "final_response"}:
                        break
                except json.JSONDecodeError:
                    print("[TRANSCRIBE] Non-JSON message received")

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


async def _run_chat_pipeline(prompt: str) -> ChatResponse:
    prompt = prompt.strip()

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


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    return await _run_chat_pipeline(payload.prompt)


def _extract_json_object(raw_text: str) -> dict:
    text = (raw_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def _summarize_gemini_error(detail: str) -> str:
    text = str(detail or "")
    try:
        payload = json.loads(text)
        err = payload.get("error") or {}
        code = err.get("code")
        status = err.get("status")
        message = str(err.get("message") or "").strip().replace("\n", " ")
        message = re.sub(r"\s+", " ", message)
        message = message[:220] + "..." if len(message) > 220 else message
        parts = ["Gemini fallback active"]
        if code:
            parts.append(f"code {code}")
        if status:
            parts.append(status)
        if message:
            parts.append(message)
        return " | ".join(parts)
    except Exception:
        clean = re.sub(r"\s+", " ", text).strip()
        clean = clean[:220] + "..." if len(clean) > 220 else clean
        return f"Gemini fallback active | {clean or 'Unknown error'}"


def _fallback_vision_summary(filename: str | None, additional_context: str) -> dict:
    source = " ".join(
        part for part in [filename or "", additional_context or ""] if part
    ).lower()

    # Build coarse labels from filename/context so we can still route a useful similarity plan.
    tokens = re.findall(r"[a-z]{3,}", source)
    stopwords = {
        "image",
        "photo",
        "jpeg",
        "jpg",
        "png",
        "trip",
        "plan",
        "travel",
    }
    labels = []
    for token in tokens:
        if token in stopwords:
            continue
        if token not in labels:
            labels.append(token)
        if len(labels) >= 5:
            break

    if not labels:
        labels = ["landmark", "architecture", "cultural site"]

    primary_subject = labels[0].replace("_", " ").title()
    return {
        "primary_subject": primary_subject,
        "landmarks": [],
        "labels": labels,
    }


async def _call_gemini_vision_with_fallback(encoded_image: str, content_type: str) -> dict:
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    key = settings.gemini_api_key

    prompt_text = (
        "Analyze this image and return ONLY valid JSON in the format: "
        '{"primary_subject":"...","landmarks":["..."],"labels":["..."]}. '
        "Use concise strings. If no landmark is clear, keep landmarks empty and infer labels."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                    {
                        "inline_data": {
                            "mime_type": content_type,
                            "data": encoded_image,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {"temperature": 0},
    }

    async def try_model(client: httpx.AsyncClient, model_name: str) -> httpx.Response:
        url = f"{base_url}/models/{model_name}:generateContent?key={key}"
        return await client.post(url, json=payload, headers={"Content-Type": "application/json"})

    candidates: list[str] = []
    if settings.gemini_vision_model:
        candidates.append(settings.gemini_vision_model)
    candidates.extend([
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ])

    # Deduplicate while preserving order.
    deduped_candidates = list(dict.fromkeys([m.strip() for m in candidates if m.strip()]))

    async with httpx.AsyncClient(timeout=30.0) as client:
        last_error_text = ""
        for model_name in deduped_candidates:
            response = await try_model(client, model_name)
            if response.status_code < 400:
                return response.json()

            last_error_text = response.text
            # Keep trying other models on 404 and 429 (free-tier/model quota issues).
            if response.status_code not in {404, 429}:
                raise HTTPException(status_code=response.status_code, detail=f"Gemini vision error: {response.text}")

        # If all direct attempts returned 404, ask ModelService for supported models.
        list_url = f"{base_url}/models?key={key}"
        list_response = await client.get(list_url)
        if list_response.status_code >= 400:
            raise HTTPException(
                status_code=list_response.status_code,
                detail=f"Gemini vision error: {last_error_text or list_response.text}",
            )

        model_items = list_response.json().get("models") or []
        discovered = []
        for item in model_items:
            name = str(item.get("name") or "")
            methods = item.get("supportedGenerationMethods") or []
            if "generateContent" in methods and name.startswith("models/"):
                short_name = name.split("/", 1)[1]
                discovered.append(short_name)

        # Prefer flash-style models for speed and free-tier friendliness.
        discovered.sort(key=lambda n: ("flash" not in n.lower(), n))

        for model_name in discovered:
            response = await try_model(client, model_name)
            if response.status_code < 400:
                return response.json()

            if response.status_code not in {404, 429}:
                raise HTTPException(status_code=response.status_code, detail=f"Gemini vision error: {response.text}")

    raise HTTPException(status_code=502, detail="Gemini vision error: no supported generateContent model was found")


@router.post("/travison", response_model=TravisonResponse)
async def travison(
    image: UploadFile = File(...),
    additional_context: str = Form(default=""),
) -> TravisonResponse:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image upload is empty")

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    content_type = image.content_type or "image/jpeg"
    quota_fallback = False
    gemini_raw_output = ""

    try:
        completion = await _call_gemini_vision_with_fallback(encoded_image, content_type)
        candidates = completion.get("candidates") or []
        parts = (((candidates[0] if candidates else {}).get("content") or {}).get("parts") or [])
        content = "\n".join(str(part.get("text") or "") for part in parts).strip()
        gemini_raw_output = content
        parsed = _extract_json_object(content)
    except HTTPException as exc:
        if exc.status_code == 429:
            parsed = _fallback_vision_summary(image.filename, additional_context)
            gemini_raw_output = _summarize_gemini_error(exc.detail)
            quota_fallback = True
        else:
            raise
    except Exception as exc:
        parsed = _fallback_vision_summary(image.filename, additional_context)
        gemini_raw_output = f"Gemini parse fallback: {exc}"
        quota_fallback = True

    landmarks = [str(item).strip() for item in (parsed.get("landmarks") or []) if str(item).strip()]
    labels = [str(item).strip() for item in (parsed.get("labels") or []) if str(item).strip()]

    primary_subject = str(parsed.get("primary_subject") or "").strip()
    if not primary_subject:
        primary_subject = landmarks[0] if landmarks else (labels[0] if labels else "landmark")
    hints = landmarks[:3] if landmarks else labels[:5]
    hint_text = ", ".join(hints) if hints else primary_subject

    planning_prompt = (
        "You are Travison, a vision-guided trip assistant.\n"
        f"Photo analysis detected: {hint_text}.\n"
        f"Primary subject: {primary_subject}.\n"
        f"Vision confidence mode: {'fallback-context' if quota_fallback else 'direct-vision'}.\n"
        "Suggest a trip plan with places similar in style, culture, architecture, or vibe to the detected subject.\n"
        "Keep the itinerary practical with time ranges and costs per person.\n"
        "Use this exact structure:\n"
        "TITLE: <short title>\n"
        "DESC: <one sentence description>\n"
        "STOP 1\n"
        "NAME: <place>\n"
        "TIME: <time range>\n"
        "COST: <cost per person>\n"
        "INFO: <short detail>\n"
        "STOP 2...\n"
        f"Additional user context: {additional_context.strip() or 'None provided.'}"
    )

    chat_result = await _run_chat_pipeline(planning_prompt)

    return TravisonResponse(
        vision=TravisonVisionSummary(
            primary_subject=primary_subject,
            landmarks=landmarks,
            labels=labels,
        ),
        vision_mode="fallback-context" if quota_fallback else "direct-vision",
        gemini_raw_output=gemini_raw_output,
        prompt_used=planning_prompt,
        result=chat_result,
    )
