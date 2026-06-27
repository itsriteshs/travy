from typing import List, Dict, Any

class CostEstimatorService:
    def estimate_itinerary_cost(
        self,
        stops: List[Dict[str, Any]],
        route_ordering: Dict[str, Any],
        budget_per_person_inr: float,
        moods: List[str],
        group_size: int = 1
    ) -> Dict[str, Any]:
        # Track categories
        food_cost = 0
        has_food_stop = False
        for s in stops:
            cat = s.get("category", "").lower()
            cost = s.get("estimated_cost_per_person_inr", s.get("estimated_cost_inr", 0))
            if cat in ["food", "restaurant", "cafe"]:
                food_cost += cost
                has_food_stop = True
                
        # Baseline minimum food cost
        if "food" in [m.lower() for m in moods] and food_cost < 150:
            food_cost = 250
        elif not has_food_stop and "food" in [m.lower() for m in moods]:
            food_cost = 200
            
        # Calculate travel costs based on total distance
        distance_meters = route_ordering.get("total_distance_meters", 5000)
        # ₹15 per km travel cost
        travel_cost = int((distance_meters / 1000.0) * 15.0)
        if travel_cost < 50:
            travel_cost = 80 # minimum travel fare
            
        # Shopping buffer
        shopping_buffer = 0
        if "shopping" in [m.lower() for m in moods]:
            shopping_buffer = 300
        else:
            shopping_buffer = 50
            
        # Miscellaneous / Buffer
        misc = 50
        
        # Tickets / Activity costs from stops
        tickets_cost = 0
        for s in stops:
            cat = s.get("category", "").lower()
            if cat not in ["food", "restaurant", "cafe", "market", "shopping"]:
                tickets_cost += s.get("estimated_cost_per_person_inr", s.get("estimated_cost_inr", 0))
                
        estimated_total_per_person = food_cost + travel_cost + shopping_buffer + misc + tickets_cost
        
        # Group calculations
        group_total = estimated_total_per_person * group_size
        total_budget_limit = budget_per_person_inr * group_size
        
        budget_status = "within_budget"
        if estimated_total_per_person > budget_per_person_inr:
            budget_status = "over_budget"
            
        budget_left_per_person = max(0, int(budget_per_person_inr - estimated_total_per_person))
        remaining_budget = max(0, int(total_budget_limit - group_total))
        
        return {
            "food": food_cost,
            "travel": travel_cost,
            "shopping_buffer": shopping_buffer,
            "misc": misc,
            "activity_cost": tickets_cost,
            "tickets": tickets_cost,
            "cost_per_person": estimated_total_per_person,
            "estimated_total": estimated_total_per_person,
            "group_total": group_total,
            "budget_left": budget_left_per_person,
            "remaining_budget": remaining_budget,
            "budget_per_person": int(budget_per_person_inr),
            "budget_status": budget_status
        }
