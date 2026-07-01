import re
from typing import Any

import httpx

from config import settings

# Persistent HTTP client – avoids per-request TCP/TLS handshake overhead.
_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=settings.otari_timeout_seconds,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


def _extract_city(prompt: str) -> str:
    m = re.search(r"in\s+([A-Za-z\s]+)", prompt)
    if m:
        return m.group(1).strip().split(" for ")[0]
    return "unknown"


def _city_guidance(city: str) -> str:
    c = city.lower().strip()

    if c in {"new delhi", "delhi", "delhi ncr"}:
        return (
            "City focus: New Delhi. Favor metro-connected routes, realistic traffic buffers, "
            "popular food and market clusters, and practical indoor alternatives for heat."
        )

    if c in {"coimbatore", "kovai"}:
        return (
            "City focus: Coimbatore. Prefer compact routing, evening-friendly stops, "
            "cafes and local food clusters, and cost-effective options for student/friend groups."
        )

    if c in {"new york", "new york city", "nyc", "manhattan", "brooklyn"}:
        return (
            "City focus: New York City. Optimize around subway-first movement, neighborhood clustering, "
            "walking fatigue control, and realistic price ranges with tax/tip awareness."
        )

    return "City focus: optimize route efficiency, budget realism, and travel fatigue."


def _resolve_model(alias: str) -> str:
    mapping = {
        "otari-small": settings.otari_small_model,
        "otari-medium": settings.otari_medium_model,
        "otari-large": settings.otari_large_model,
        "otari-vision": settings.otari_vision_model,
    }
    return mapping.get(alias, settings.otari_medium_model)


def _chat_completions_url() -> str:
    base = settings.otari_base_url.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _extract_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices", [])
    if not choices:
        return ""

    message = choices[0].get("message", {})
    content = message.get("content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return "\n".join(part for part in text_parts if part).strip()

    return ""


async def generate_itinerary(prompt: str, model: str, mcpd_context: dict[str, Any]) -> str:
    if not settings.otari_api_key:
        return "Otari is not configured. Set OTARI_API_KEY in backend/.env."

    city = _extract_city(prompt)
    model_name = _resolve_model(model)

    system_prompt = (
        "You are Travy, a travel itinerary generator. "
        "Return ONLY a structured itinerary in EXACTLY this format (no extra text before or after):\n\n"
        "TITLE: <2-5 word catchy plan name>\n"
        "DESC: <one sentence description of the plan>\n\n"
        "STOP 1\n"
        "NAME: <place name>\n"
        "TIME: <HH:MM AM - HH:MM AM>\n"
        "COST: <amount/person e.g. ₹300/person or $5/person>\n"
        "INFO: <one sentence describing the stop and what to do there>\n\n"
        "STOP 2\n"
        "NAME: <place name>\n"
        "TIME: <HH:MM AM - HH:MM AM>\n"
        "COST: <amount/person>\n"
        "INFO: <one sentence>\n\n"
        "(Continue for 3-6 stops total)\n\n"
        "SUMMARY: <2 sentence summary of the full plan>\n\n"
        "Rules: Use 3 to 6 stops. Keep times realistic and sequential. "
        "Costs in local currency of the city. One INFO sentence per stop only. "
        "Do not add any text outside the format above. "
        f"{_city_guidance(city)}"
    )

    user_prompt = (
        "Generate a structured travel plan from this user request.\n\n"
        f"User request:\n{prompt}\n\n"
        "Tool context:\n"
        f"Weather: {mcpd_context.get('weather', '')}\n"
        f"Places: {', '.join(mcpd_context.get('places', []))}\n"
        f"Map: {mcpd_context.get('map', '')}\n"
        f"Budget helper: {mcpd_context.get('budget', '')}\n\n"
        "Return ONLY the structured TITLE / STOP blocks / SUMMARY format. "
        "No extra text, no markdown headers, no bullet points outside INFO lines."
    )

    body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
    }

    headers = {
        "Authorization": f"Bearer {settings.otari_api_key}",
        "Content-Type": "application/json",
    }

    try:
        client = _get_client()
        response = await client.post(_chat_completions_url(), headers=headers, json=body)
        response.raise_for_status()
        data = response.json()

        text = _extract_text(data)
        if text:
            return text

        return "Otari returned an empty response. Try rephrasing the request."
    except httpx.HTTPStatusError as exc:
        return f"Otari request failed: HTTP {exc.response.status_code}."
    except httpx.RequestError as exc:
        return f"Otari network error: {exc}."
    except Exception as exc:
        return f"Otari request failed: {type(exc).__name__}."
