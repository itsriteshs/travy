from typing import List, Dict, Any

class CostEstimatorService:
    def estimate_itinerary_cost(
        self,
        stops: List[Dict[str, Any]],
        route_ordering: Dict[str, Any],
        budget_per_person_inr: float,
        moods: List[str]
    ) -> Dict[str, Any]:
        # Calculate food costs from stops that are food-related
        food_cost = 0
        has_food_stop = False
        for s in stops:
            cat = s.get("category", "").lower()
            cost = s.get("estimated_cost_per_person_inr", s.get("estimated_cost_inr", 0))
            if cat in ["food", "restaurant", "cafe"]:
                food_cost += cost
                has_food_stop = True
            elif cost > 0 and cat not in ["market", "shopping"]:
                # entrance fees etc.
                pass
                
        # Default minimum food cost if they want food but didn't select many high-cost places
        if "food" in [m.lower() for m in moods] and food_cost < 150:
            food_cost = 250
        elif not has_food_stop and "food" in [m.lower() for m in moods]:
            food_cost = 200
            
        # Calculate travel costs based on total distance
        distance_meters = route_ordering.get("total_distance_meters", 5000)
        # Assume ₹15 per km travel cost
        travel_cost = int((distance_meters / 1000.0) * 15.0)
        if travel_cost < 50:
            travel_cost = 80 # minimum travel fare
            
        # Calculate shopping buffer
        shopping_buffer = 0
        if "shopping" in [m.lower() for m in moods]:
            shopping_buffer = 300
        else:
            shopping_buffer = 50
            
        # Miscellaneous
        misc = 50
        
        # Entrance fees/activity costs from stops
        activity_cost = 0
        for s in stops:
            cat = s.get("category", "").lower()
            if cat not in ["food", "restaurant", "cafe", "market", "shopping"]:
                activity_cost += s.get("estimated_cost_per_person_inr", s.get("estimated_cost_inr", 0))
                
        estimated_total = food_cost + travel_cost + shopping_buffer + misc + activity_cost
        
        budget_status = "within_budget"
        if estimated_total > budget_per_person_inr:
            budget_status = "over_budget"
            
        budget_left = max(0, int(budget_per_person_inr - estimated_total))
        
        return {
            "food": food_cost,
            "travel": travel_cost,
            "shopping_buffer": shopping_buffer,
            "misc": misc,
            "activity_cost": activity_cost,
            "estimated_total": estimated_total,
            "budget_left": budget_left,
            "budget_per_person": int(budget_per_person_inr),
            "budget_status": budget_status
        }
