class IntentClassifierService:
    def classify(self, prompt: str, is_malicious: bool) -> dict:
        if is_malicious:
            return {
                "type": "malicious",
                "confidence": 1.0,
                "reason": "Suspicious security patterns detected in prompt."
            }
            
        p = prompt.lower()
        
        # Check out of scope booking requests
        if any(w in p for w in ["book", "pay", "reserve", "ticket", "purchase", "booking"]):
            return {
                "type": "booking_request",
                "confidence": 0.95,
                "reason": "User is asking for booking or reservation services, which are out of scope."
            }
            
        # Check unsupported live data
        if any(w in p for w in ["live crime", "crime data", "live traffic", "traffic data", "real-time crime"]):
            return {
                "type": "unsupported_live_data",
                "confidence": 0.9,
                "reason": "User requested live/real-time crime or traffic data which is not supported."
            }
            
        # Check budget math
        if any(w in p for w in ["math", "calculate", "how much", "budget math", "₹", "rs.", "usd"]):
            # If it's a simple math question, budget_math
            if "?" in p or any(w in p for w in ["each for", "per person", "will be"]):
                if not any(w in p for w in ["plan", "itinerary"]):
                    return {
                        "type": "budget_math",
                        "confidence": 0.85,
                        "reason": "User is asking for pricing or budget calculation."
                    }
                    
        # Check route comfort
        if any(w in p for w in ["safest route", "comfort", "tiring", "walking fatigue"]):
            if not any(w in p for w in ["plan", "itinerary"]):
                return {
                    "type": "route_comfort",
                    "confidence": 0.8,
                    "reason": "User is asking about route comfort or fatigue constraints."
                }
                
        # Check local discovery
        if any(w in p for w in ["find", "discover", "explore", "what to do in", "places near"]):
            if not any(w in p for w in ["plan", "itinerary"]):
                return {
                    "type": "local_discovery",
                    "confidence": 0.85,
                    "reason": "User is seeking point of interest recommendations."
                }
                
        # Default fallback to travel planning if any travel terms are present
        travel_terms = ["plan", "delhi", "bangalore", "jaipur", "mumbai", "friends", "visit", "trip", "itinerary", "route", "solo", "couple", "family"]
        if any(w in p for w in travel_terms) or len(p.split()) > 3:
            return {
                "type": "travel_planning",
                "confidence": 0.92,
                "reason": "Prompt indicates travel planning request."
            }
            
        return {
            "type": "out_of_scope",
            "confidence": 0.5,
            "reason": "Could not determine a supported travel intent."
        }
