import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core import demo_state
from app.services.injection_service import InjectionService
from app.services.intent_classifier_service import IntentClassifierService
from app.services.parser_service import ParserService
from app.services.otari_extractor_service import OtariExtractorService
from app.services.complexity_service import ComplexityService
from app.services.budget_service import BudgetService
from app.services.context_service import ContextService
from app.services.router_engine import RouterEngine
from app.services.trace_service import TraceService
from app.services.persistence_service import PersistenceService
from app.services.itinerary_generation_service import ItineraryGenerationService
from app.services.geocoding_service import GeocodingService
from app.services.candidate_builder_service import CandidateBuilderService

router = APIRouter()

class AnalyzeRequest(BaseModel):
    prompt: str
    budget_mode: Optional[str] = None
    session_id: Optional[str] = "demo"

class GenerateRequest(BaseModel):
    request_id: str
    session_id: Optional[str] = "demo"

class DemoModeRequest(BaseModel):
    mode: str

@router.post("/api/planner/analyze")
async def analyze_request(request: AnalyzeRequest):
    prompt = request.prompt
    session_id = request.session_id or "demo"
    # Use specified budget mode, or fallback to demo state
    budget_mode = request.budget_mode or demo_state.current_demo_mode
    if budget_mode not in ["healthy", "low", "critical", "auto"]:
        budget_mode = "healthy"
        
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    
    # Save the initial request log
    PersistenceService.save_request(request_id, session_id, prompt, budget_mode)
    
    # 1. Security Scan
    sec_service = InjectionService()
    security = sec_service.scan(prompt)
    
    PersistenceService.save_trace(
        request_id, 1, "Prompt injection scan", "LOCAL_LOGIC",
        "safe" if security["safe"] else "blocked", 0.0,
        "No suspicious instruction detected." if security["safe"] else f"Suspicious phrases detected: {security['detected']}"
    )
    
    # 2. Intent Classification
    intent_service = IntentClassifierService()
    intent = intent_service.classify(prompt, not security["safe"])
    
    PersistenceService.save_trace(
        request_id, 2, "Intent classification", "LOCAL_LOGIC",
        intent["type"], 0.0, intent["reason"]
    )
    
    # 3. Dynamic Parser
    parser_service = ParserService()
    parsed = parser_service.parse(prompt)
    
    # Set default sources for parsed fields
    for k in parsed:
        parsed[k]["source"] = "local_parser"
        
    # Re-calculate missing required fields
    missing_fields = []
    if not parsed["city"]["value"]:
        missing_fields.append("city")
    if not parsed["group_size"]["value"]:
        missing_fields.append("group_size")
    if not parsed["budget_per_person_inr"]["value"]:
        missing_fields.append("budget_per_person")
    if not parsed["start_time"]["value"] or not parsed["end_time"]["value"]:
        missing_fields.append("time_window")
    if not parsed["moods"]["value"]:
        missing_fields.append("moods")
        
    # 4. Optional Cheap Otari Extractor
    used_otari_extractor = False
    otari_success = True
    if security["safe"] and budget_mode != "critical" and missing_fields:
        extractor = OtariExtractorService()
        extract_result = await extractor.extract(prompt)
        if extract_result["success"]:
            used_otari_extractor = True
            ext_data = extract_result["extracted"]
            for key, field_name in [
                ("city", "city"),
                ("current_location", "current_location"),
                ("group_size", "group_size"),
                ("budget_per_person_inr", "budget_per_person_inr"),
                ("start_time", "start_time"),
                ("end_time", "end_time"),
                ("moods", "moods"),
                ("energy", "energy"),
                ("transport", "transport"),
                ("dietary_restrictions", "dietary_restrictions"),
                ("weather_conditions", "weather_conditions"),
                ("accessibility_requirements", "accessibility_requirements"),
                ("safety_preferences", "safety_preferences"),
                ("crowd_tolerance", "crowd_tolerance")
            ]:
                val = ext_data.get(key)
                if val is not None and (field_name not in parsed or not parsed[field_name]["value"] or parsed[field_name]["confidence"] < 0.8):
                    parsed[field_name] = {
                        "value": val,
                        "confidence": 0.90,
                        "source": "otari_cheap_extractor"
                    }
                    
            # Reevaluate missing fields after Otari extractor run
            missing_fields = []
            if not parsed.get("city", {}).get("value"):
                missing_fields.append("city")
            if not parsed.get("group_size", {}).get("value"):
                missing_fields.append("group_size")
            if not parsed.get("budget_per_person_inr", {}).get("value"):
                missing_fields.append("budget_per_person")
            if not parsed.get("start_time", {}).get("value") or not parsed.get("end_time", {}).get("value"):
                missing_fields.append("time_window")
            if not parsed.get("moods", {}).get("value"):
                missing_fields.append("moods")
        else:
            if extract_result.get("used_otari"):
                used_otari_extractor = True
                otari_success = False
    # 4.5 Default fallbacks if city is present to prevent blocking
    if parsed.get("city", {}).get("value"):
        if not parsed.get("group_size", {}).get("value"):
            parsed["group_size"] = {"value": 1, "confidence": 0.80, "source": "default_fallback"}
        if not parsed.get("budget_per_person_inr", {}).get("value"):
            parsed["budget_per_person_inr"] = {"value": 1000, "confidence": 0.80, "source": "default_fallback"}
        if not parsed.get("start_time", {}).get("value") or not parsed.get("end_time", {}).get("value"):
            parsed["start_time"] = {"value": "10 AM", "confidence": 0.80, "source": "default_fallback"}
            parsed["end_time"] = {"value": "6 PM", "confidence": 0.80, "source": "default_fallback"}
        if not parsed.get("moods", {}).get("value"):
            parsed["moods"] = {"value": ["sightseeing", "food"], "confidence": 0.80, "source": "default_fallback"}
        missing_fields = []

    # 5. Overall confidence calculation
    total_conf = sum(parsed[k]["confidence"] for k in parsed)
    overall_confidence = round(total_conf / len(parsed), 2)
    
    PersistenceService.save_trace(
        request_id, 3, "Constraint parsing", "LOCAL_PARSER" if not used_otari_extractor else "OTARI_CHEAP_EXTRACTOR",
        "high_confidence" if overall_confidence >= 0.8 else "low_confidence", 0.0,
        "Required fields extracted locally." if overall_confidence >= 0.8 else "Vague or missing planning constraints."
    )
    
    # 6. Complexity scoring
    complexity_service = ComplexityService()
    complexity = complexity_service.calculate(parsed, overall_confidence)
    
    # 7. Budget ledger lookup
    budget_service = BudgetService()
    budget_ledger = budget_service.get_ledger(budget_mode)
    
    # 8. Context prioritizing
    context_service = ContextService()
    context = context_service.select_context(budget_mode)
    
    PersistenceService.save_trace(
        request_id, 4, "Context selection", "LOCAL_LOGIC",
        "api_only_fallback" if budget_mode == "critical" else ("low_budget" if budget_mode == "low" else "full_context"),
        0.0, f"Budget mode is {budget_mode}."
    )
    
    # 9. Route decision
    router_engine = RouterEngine()
    route_decision = router_engine.decide_route(
        security=security,
        intent=intent,
        parsed=parsed,
        complexity=complexity,
        budget=budget_ledger,
        missing_fields=missing_fields
    )
    
    # Update budget ledger estimated cost
    budget_ledger["estimated_request_cost_usd"] = route_decision["estimated_cost_usd"]
    
    # Determine next action
    next_action = "generate"
    if not security["safe"]:
        next_action = "block"
    elif intent["type"] == "booking_request":
        next_action = "out_of_scope"
    elif intent["type"] == "unsupported_live_data":
        next_action = "fallback"
    elif missing_fields:
        next_action = "clarify"
    elif budget_mode == "critical":
        next_action = "fallback"
        
    PersistenceService.save_trace(
        request_id, 5, "Model route selection", route_decision["route"],
        "selected_for_phase_3" if next_action in ["generate", "fallback"] else "fallback_or_blocked",
        route_decision["estimated_cost_usd"], route_decision["reason"]
    )
    
    # Assemble response
    response_data = {
        "request_id": request_id,
        "next_action": next_action,
        "security": security,
        "intent": intent,
        "parsed": parsed,
        "missing_fields": missing_fields,
        "parser": {
            "overall_confidence": overall_confidence,
            "used_otari_extractor": used_otari_extractor,
            "otari_success": otari_success,
            "reason": "Local parser found all required fields with high confidence." if not used_otari_extractor else ("Otari extractor succeeded." if otari_success else "Otari extractor failed or was unreachable.")
        },
        "complexity": complexity,
        "budget": budget_ledger,
        "context": context,
        "route_decision": route_decision,
        "routing_trace": PersistenceService.get_traces(request_id)
    }
    
    # Save the parsed analysis output
    PersistenceService.save_analysis(
        analysis_id=f"ana_{uuid.uuid4().hex[:8]}",
        request_id=request_id,
        security=security,
        intent=intent,
        parsed=parsed,
        missing_fields=missing_fields,
        complexity=complexity,
        budget=budget_ledger,
        context=context,
        route_decision=route_decision
    )
    
    # Increment usage stats
    demo_state.total_requests += 1
    demo_state.total_cost_usd += route_decision["estimated_cost_usd"]
    
    return response_data

@router.post("/api/planner/generate")
async def generate_itinerary(request: GenerateRequest):
    request_id = request.request_id
    session_id = request.session_id or "demo"
    generator = ItineraryGenerationService()
    try:
        result = await generator.generate(request_id, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/results/{request_id}")
def get_results(request_id: str):
    itinerary = PersistenceService.get_itinerary(request_id)
    if not itinerary:
        # Check if analyze request exists. If it exists but wasn't generated yet,
        # we can trigger generation automatically or tell frontend to POST /generate
        analysis = PersistenceService.get_analysis(request_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No results found for request {request_id}")
        return {"status": "pending_generation", "request_id": request_id}
    return itinerary

@router.get("/api/places/search")
async def search_places(city: str, moods: str = ""):
    geocoder = GeocodingService()
    builder = CandidateBuilderService()
    try:
        city_geo = await geocoder.geocode_city(city)
        mood_list = [m.strip() for m in moods.split(",") if m.strip()]
        candidates = await builder.get_candidates(city_geo, mood_list)
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/router/usage")
def get_usage():
    # Retrieve active demo state usage from budget ledger
    summary = PersistenceService.get_budget_ledger_summary("demo")
    mode = demo_state.current_demo_mode
    if mode == "low":
        summary["remaining_usd"] = 0.12
        summary["actual_used_usd"] = 1.88
    elif mode == "critical":
        summary["remaining_usd"] = 0.02
        summary["actual_used_usd"] = 1.98
        
    return {
        "total_requests": demo_state.total_requests,
        "budget_remaining_usd": summary["remaining_usd"],
        "total_cost_usd": summary["actual_used_usd"]
    }

@router.get("/api/router/trace/{request_id}")
def get_trace_by_id(request_id: str):
    traces = PersistenceService.get_traces(request_id)
    return traces

@router.post("/api/demo/mode")
def set_demo_mode(request: DemoModeRequest):
    mode = request.mode
    if mode in ["healthy", "low", "critical", "auto"]:
        demo_state.current_demo_mode = mode
        return {"status": "ok", "mode": mode}
    return {"status": "error", "message": f"Invalid mode: {mode}"}
