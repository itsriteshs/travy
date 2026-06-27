from app.services.budget_ledger_service import BudgetLedgerService

class BudgetService:
    def get_ledger(self, mode: str) -> dict:
        return BudgetLedgerService.get_ledger_summary(session_id="demo", mode=mode)
