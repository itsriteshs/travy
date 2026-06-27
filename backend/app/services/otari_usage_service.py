from typing import Dict, Any
from app.services.persistence_service import PersistenceService
from app.core import demo_state

class OtariUsageService:
    def get_router_usage(self, session_id: str = "demo") -> Dict[str, Any]:
        summary = PersistenceService.get_budget_ledger_summary(session_id)
        
        # Override budget metrics if special demo modes are active
        mode = demo_state.current_demo_mode
        if mode == "low":
            summary["remaining_usd"] = 0.12
            summary["actual_used_usd"] = 1.88
            summary["total_budget_usd"] = 2.0
        elif mode == "critical":
            summary["remaining_usd"] = 0.02
            summary["actual_used_usd"] = 1.98
            summary["total_budget_usd"] = 2.0
            
        last_call = summary.get("last_call")
        
        return {
            "total_budget_usd": summary["total_budget_usd"],
            "estimated_used_usd": summary["estimated_used_usd"],
            "actual_used_usd": summary["actual_used_usd"],
            "remaining_usd": summary["remaining_usd"],
            "usage_source": "otari_response_usage_fields" if last_call else "local_estimate_from_recorded_calls",
            "live_usage_available": True,
            "last_call": last_call
        }
