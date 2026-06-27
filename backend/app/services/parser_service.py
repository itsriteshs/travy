import re

class ParserService:
    def parse(self, prompt: str) -> dict:
        p = prompt.lower()
        
        # 1. City extraction
        cities = ["delhi", "bangalore", "jaipur", "mumbai", "goa", "pune", "hyderabad", "chennai", "kolkata"]
        city_val = None
        city_conf = 0.0
        for city in cities:
            if city in p:
                city_val = city.capitalize()
                city_conf = 0.96
                break
        
        if not city_val:
            # Fallback check for in/plan/visit
            match = re.search(r'(?:in|plan|visit|at)\s+([a-z][a-z0-9\-]+)', p, re.IGNORECASE)
            if match:
                extracted_word = match.group(1).lower()
                ignore_words = [
                    "something", "fun", "a", "to", "with", "for", "this", "that", "my", "our", 
                    "your", "the", "me", "friends", "plan", "visit", "trip", "cafe", "place", 
                    "places", "everything", "anyone", "someone", "some"
                ]
                if extracted_word not in ignore_words:
                    city_val = extracted_word.capitalize()
                    city_conf = 0.75
        
        # 2. Group size extraction
        group_size_val = None
        group_size_conf = 0.0
        
        if "me and " in p and "friend" in p:
            match = re.search(r'me\s+and\s+(\d+)\s+friend', p)
            if match:
                group_size_val = int(match.group(1)) + 1
                group_size_conf = 0.95
        
        if not group_size_val:
            match = re.search(r'(\d+)\s+(?:friends|people|persons|members|of us)', p)
            if match:
                group_size_val = int(match.group(1))
                group_size_conf = 0.95
            
        if not group_size_val:
            match = re.search(r'group\s+of\s+(\d+)', p)
            if match:
                group_size_val = int(match.group(1))
                group_size_conf = 0.95
                
        if not group_size_val:
            match = re.search(r'we\s+are\s+(\d+)', p)
            if match:
                group_size_val = int(match.group(1))
                group_size_conf = 0.90
                
        if not group_size_val:
            if "couple" in p or "two of us" in p:
                group_size_val = 2
                group_size_conf = 0.90
            elif "solo" in p or "alone" in p or "myself" in p:
                group_size_val = 1
                group_size_conf = 0.90
            elif "family of five" in p:
                group_size_val = 5
                group_size_conf = 0.95
                
        # 3. Budget extraction (₹800 each, 800 per person, under ₹500, budget 1k each)
        budget_val = None
        budget_conf = 0.0
        
        # First check "1k" style
        match_k = re.search(r'(\d+)\s*k(?:\s*(?:each|per person|pp))?', p)
        if match_k:
            budget_val = int(match_k.group(1)) * 1000
            budget_conf = 0.90
            
        if not budget_val:
            # Check standard prefix (₹ / rs)
            match = re.search(r'(?:₹|rs\.?|rs|budget)\s*(\d+(?:\.\d+)?)\s*(?:each|per person|pp)?', p)
            if not match:
                # Check suffix (each / per person / pp)
                match = re.search(r'(\d+(?:\.\d+)?)\s*(?:each|per person|pp|inr|usd|buffer)', p)
                
            if match:
                budget_val = int(float(match.group(1)))
                budget_conf = 0.94
                
        if not budget_val:
            if "cheap" in p:
                budget_val = 500  # Default cheap placeholder
                budget_conf = 0.70
                
        # 4. Start & End times
        start_time_val = None
        end_time_val = None
        time_conf = 0.0
        
        match = re.search(r'(\d+)\s*(pm|am)?\s*(?:to|-)\s*(\d+)\s*(pm|am)', p)
        if match:
            first_num = match.group(1)
            first_am_pm_match = re.search(r'(\d+)\s*(pm|am)', p[:match.end(1)+3])
            first_am_pm = first_am_pm_match.group(2) if first_am_pm_match else match.group(4)
            
            start_time_val = f"{first_num} {first_am_pm.upper()}"
            end_time_val = f"{match.group(3)} {match.group(4).upper()}"
            time_conf = 0.91
        elif "tonight" in p:
            start_time_val = "6 PM"
            end_time_val = "10 PM"
            time_conf = 0.80
        elif "evening" in p:
            start_time_val = "4 PM"
            end_time_val = "8 PM"
            time_conf = 0.80
        elif "morning" in p:
            start_time_val = "9 AM"
            end_time_val = "1 PM"
            time_conf = 0.80
            
        # 5. Moods extraction
        moods_list = ["shopping", "food", "cafe", "photos", "sightseeing", "chill", "music", "events", "monuments", "street food", "markets"]
        detected_moods = []
        for mood in moods_list:
            if mood in p:
                detected_moods.append(mood)
        moods_val = detected_moods if detected_moods else []
        moods_conf = 0.88 if detected_moods else 0.0
        
        # 6. Energy/Fatigue preference
        energy_val = "medium"
        energy_conf = 0.50
        if any(w in p for w in ["not too tiring", "low energy", "relaxing", "chill"]):
            energy_val = "medium-low"
            energy_conf = 0.82
        elif any(w in p for w in ["active", "tiring", "lots of walking", "high energy"]):
            energy_val = "high"
            energy_conf = 0.82
            
        # 7. Transport preference
        transport_val = "mixed"
        transport_conf = 0.50
        if "cab" in p or "taxi" in p:
            transport_val = "cab"
            transport_conf = 0.80
        elif "metro" in p or "subway" in p:
            transport_val = "metro"
            transport_conf = 0.80
        elif "walk" in p:
            transport_val = "walk"
            transport_conf = 0.80
            
        # 8. Crowd tolerance
        crowd_val = "medium"
        crowd_conf = 0.50
        if "quiet" in p or "no crowd" in p or "avoid crowd" in p:
            crowd_val = "low"
            crowd_conf = 0.80
            
        return {
            "city": {"value": city_val, "confidence": city_conf},
            "group_size": {"value": group_size_val, "confidence": group_size_conf},
            "budget_per_person_inr": {"value": budget_val, "confidence": budget_conf},
            "start_time": {"value": start_time_val, "confidence": time_conf},
            "end_time": {"value": end_time_val, "confidence": time_conf},
            "moods": {"value": moods_val, "confidence": moods_conf},
            "energy": {"value": energy_val, "confidence": energy_conf},
            "transport": {"value": transport_val, "confidence": transport_conf},
            "crowd_tolerance": {"value": crowd_val, "confidence": crowd_conf}
        }
