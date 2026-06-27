from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.demo_orchestrator_service import DemoOrchestratorService
from app.services.persistence_service import PersistenceService
from app.services.api_call_logger_service import ApiCallLoggerService
from app.api.planner import analyze_request, generate_itinerary, AnalyzeRequest, GenerateRequest
from app.core import demo_state

router = APIRouter()

class RunScenarioRequest(BaseModel):
    scenario: str
    session_id: Optional[str] = "demo"

@router.get("/api/demo/status")
def get_demo_status():
    return {
        "current_demo_mode": demo_state.current_demo_mode,
        "total_requests": demo_state.total_requests,
        "total_cost_usd": demo_state.total_cost_usd
    }

@router.post("/api/demo/reset")
def reset_demo():
    DemoOrchestratorService.reset_demo_state()
    return {"status": "ok", "message": "Demo state and DB logs reset successfully."}

@router.post("/api/demo/run-scenario")
async def run_scenario(request: RunScenarioRequest):
    scenario_name = request.scenario
    session_id = request.session_id or "demo"
    
    # 1. Fetch scenario params
    info = DemoOrchestratorService.get_scenario_prompt(scenario_name)
    prompt = info["prompt"]
    budget_mode = info["budget_mode"]
    
    # Force demo budget mode state
    demo_state.current_demo_mode = budget_mode
    
    # 2. Run analysis
    analyze_data = await analyze_request(AnalyzeRequest(
        prompt=prompt,
        budget_mode=budget_mode,
        session_id=session_id
    ))
    
    request_id = analyze_data["request_id"]
    next_action = analyze_data["next_action"]
    
    generation_data = None
    if next_action == "generate":
        # 3. Run generation automatically
        generation_data = await generate_itinerary(GenerateRequest(
            request_id=request_id,
            session_id=session_id
        ))
        
    return {
        "status": "ok",
        "scenario": scenario_name,
        "request_id": request_id,
        "next_action": next_action,
        "analysis": analyze_data,
        "generation": generation_data
    }

@router.get("/api/sessions/{session_id}/requests")
def get_session_requests(session_id: str):
    return PersistenceService.get_all_requests_and_results(session_id)

@router.get("/api/sessions/{session_id}/results")
def get_session_results(session_id: str):
    data = PersistenceService.get_all_requests_and_results(session_id)
    return data["results"]

@router.get("/api/debug/api-calls/{request_id}")
def get_api_calls(request_id: str):
    service = ApiCallLoggerService()
    return service.get_logs_for_request(request_id)
