from typing import Dict, Any, Optional
from app.services.persistence_service import PersistenceService
from app.core.config import settings

class BudgetLedgerService:
    @staticmethod
    def get_ledger_summary(session_id: str = "demo", mode: Optional[str] = None) -> Dict[str, Any]:
        summary = PersistenceService.get_budget_ledger_summary(session_id)
        total_budget = float(summary.get("total_budget_usd") or settings.DAILY_BUDGET_USD)
        used_budget = float(summary.get("actual_used_usd") or 0.0)
        remaining = max(0.0, total_budget - used_budget)

        active_mode = mode or "auto"
        if active_mode == "auto":
            ratio = remaining / total_budget if total_budget else 0.0
            if ratio <= 0.05:
                active_mode = "critical"
            elif ratio <= 0.25:
                active_mode = "low"
            else:
                active_mode = "healthy"
            
        return {
            "mode": active_mode,
            "total_budget_usd": total_budget,
            "used_budget_usd": used_budget,
            "remaining_budget_usd": remaining,
            "estimated_request_cost_usd": 0.0,
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
