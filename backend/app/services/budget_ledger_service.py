from typing import Dict, Any, Optional
from app.services.persistence_service import PersistenceService
from app.core import demo_state

class BudgetLedgerService:
    @staticmethod
    def get_ledger_summary(session_id: str = "demo", mode: Optional[str] = None) -> Dict[str, Any]:
        # Fetch DB metrics
        summary = PersistenceService.get_budget_ledger_summary(session_id)
        
        # Use passed mode, or fallback to demo state
        active_mode = mode or demo_state.current_demo_mode
        if active_mode == "low":
            summary["remaining_usd"] = 0.12
            summary["actual_used_usd"] = 1.88
            summary["total_budget_usd"] = 2.0
        elif active_mode == "critical":
            summary["remaining_usd"] = 0.02
            summary["actual_used_usd"] = 1.98
            summary["total_budget_usd"] = 2.0
            
        return {
            "mode": active_mode,
            "total_budget_usd": summary["total_budget_usd"],
            "used_budget_usd": summary["actual_used_usd"],
            "remaining_budget_usd": summary["remaining_usd"],
            "estimated_request_cost_usd": 0.0, # Filled in router later
            "last_call": summary.get("last_call")
        }

    @staticmethod
    def record_cost(
        ledger_id: str,
        session_id: str,
        request_id: str,
        provider: str,
        model_id: str,
        estimated_cost_usd: float,
        actual_cost_usd: float,
        usage_source: str,
        input_tokens: int,
        output_tokens: int
    ):
        PersistenceService.save_budget_ledger(
            ledger_id=ledger_id,
            session_id=session_id,
            request_id=request_id,
            provider=provider,
            model_id=model_id,
            estimated_cost_usd=estimated_cost_usd,
            actual_cost_usd=actual_cost_usd,
            usage_source=usage_source,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
