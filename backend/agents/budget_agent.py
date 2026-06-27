from budget.budget_manager import BudgetManager


class BudgetAgent:
    def __init__(self, manager: BudgetManager) -> None:
        self.manager = manager

    def validate(self, estimated_cost: float, selected_model: str) -> tuple[str, float, bool, bool]:
        return self.manager.enforce(estimated_cost, selected_model)
