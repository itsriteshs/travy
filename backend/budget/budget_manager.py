from threading import Lock


class BudgetManager:
    def __init__(self, initial_budget: float) -> None:
        self._initial_budget = initial_budget
        self._spent = 0.0
        self._lock = Lock()

    def remaining(self) -> float:
        with self._lock:
            return round(max(0.0, self._initial_budget - self._spent), 6)

    def total_spend(self) -> float:
        with self._lock:
            return round(self._spent, 6)

    def enforce(self, estimated_cost: float, selected_model: str) -> tuple[str, float, bool, bool]:
        with self._lock:
            remaining_budget = max(0.0, self._initial_budget - self._spent)

            if remaining_budget <= 0:
                return "otari-small", 0.0, True, True

            downgraded = False
            final_model = selected_model
            final_cost = estimated_cost

            if estimated_cost > remaining_budget:
                downgraded = True
                final_model = "otari-small"
                final_cost = min(remaining_budget, estimated_cost * 0.35)

            if final_cost > remaining_budget:
                final_cost = remaining_budget

            self._spent += final_cost
            exhausted = self._spent >= self._initial_budget
            return final_model, round(final_cost, 6), downgraded, exhausted
