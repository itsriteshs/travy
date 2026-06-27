import re

class ParserService:
    def parse(self, prompt: str) -> dict:
        p = prompt.lower()
        
        # 1. City extraction
        cities = ["delhi", "bangalore", "jaipur", "mumbai", "goa", "pune", "hyderabad", "chennai", "kolkata", "new york", "nyc", "london", "paris", "tokyo"]
        city_val = None
        city_conf = 0.0
        for city in cities:
            if city in p:
                city_val = city.capitalize()
                city_conf = 0.96
                break
        
        if not city_val:
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
        
        # 2. Current location extraction
        current_loc_val = None
        current_loc_conf = 0.0
        if "near me" in p or "my location" in p:
            current_loc_val = "user_location_gps"
            current_loc_conf = 0.85
        elif "from my hotel" in p:
            current_loc_val = "user_hotel"
            current_loc_conf = 0.80
            
        # 3. Group size extraction
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
            if "solo" in p or "myself" in p:
                group_size_val = 1
                group_size_conf = 0.90
            elif "couple" in p or "two of us" in p:
                group_size_val = 2
                group_size_conf = 0.90
                
        # 4 & 5. Budget and Budget per person
        budget_val = None
        budget_conf = 0.0
        # ₹800 each / rs 800 per person / budget 1k each
        match = re.search(r'(?:₹|rs\.?|rs|budget)\s*(\d+(?:\.\d+)?)\s*(k|thousand)?\s*(?:each|per person|pp)?', p)
        if match:
            val = float(match.group(1))
            suffix = match.group(2)
            if suffix == "k":
                val *= 1000
            elif suffix == "thousand":
                val *= 1000
            budget_val = int(val)
            budget_conf = 0.90

            
        # 6. Available Time
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
        elif "evening" in p:
            start_time_val = "4 PM"
            end_time_val = "8 PM"
            time_conf = 0.80
        elif "morning" in p:
            start_time_val = "9 AM"
            end_time_val = "1 PM"
            time_conf = 0.80
            
        # 7. Transportation method
        transport_val = "mixed"
        transport_conf = 0.50
        if "cab" in p or "taxi" in p:
            transport_val = "cab"
            transport_conf = 0.80
        elif "metro" in p:
            transport_val = "metro"
            transport_conf = 0.80
        elif "walk" in p:
            transport_val = "walk"
            transport_conf = 0.80
            
        # 8 & 9. Preferences and Activity types
        moods_list = ["shopping", "food", "cafe", "photos", "sightseeing", "chill", "music", "events", "monuments"]
        detected_moods = []
        for mood in moods_list:
            if mood in p:
                detected_moods.append(mood)
        moods_val = detected_moods if detected_moods else []
        moods_conf = 0.88 if detected_moods else 0.0
        
        # 10. Pace / Energy
        energy_val = "medium"
        energy_conf = 0.50
        if "not too tiring" in p or "relaxing" in p or "chill" in p:
            energy_val = "medium-low"
            energy_conf = 0.82
        elif "active" in p or "high energy" in p:
            energy_val = "high"
            energy_conf = 0.82
            
        # 11. Dietary Restrictions
        dietary_val = []
        dietary_conf = 0.0
        for restriction in ["vegan", "vegetarian", "veg", "halal", "kosher", "gluten-free", "gluten free"]:
            if restriction in p:
                dietary_val.append(restriction)
                dietary_conf = 0.85
                
        # 12. Weather Conditions
        weather_val = None
        weather_conf = 0.0
        for cond in ["rain", "rainy", "hot", "sunny", "cold", "windy", "snow"]:
            if cond in p:
                weather_val = cond
                weather_conf = 0.85
                
        # 13. Accessibility Requirements
        access_val = []
        access_conf = 0.0
        for req in ["wheelchair", "accessible", "no stairs", "elevator"]:
            if req in p:
                access_val.append(req)
                access_conf = 0.90
                
        # 14. Safety Preferences
        safety_val = "standard"
        safety_conf = 0.50
        if "safe" in p or "well-lit" in p or "avoid crowd" in p:
            safety_val = "high_comfort"
            safety_conf = 0.80

        return {
            "city": {"value": city_val, "confidence": city_conf},
            "current_location": {"value": current_loc_val, "confidence": current_loc_conf},
            "budget_per_person_inr": {"value": budget_val, "confidence": budget_conf},
            "group_size": {"value": group_size_val, "confidence": group_size_conf},
            "start_time": {"value": start_time_val, "confidence": time_conf},
            "end_time": {"value": end_time_val, "confidence": time_conf},
            "moods": {"value": moods_val, "confidence": moods_conf},
            "energy": {"value": energy_val, "confidence": energy_conf},
            "transport": {"value": transport_val, "confidence": transport_conf},
            "dietary_restrictions": {"value": dietary_val, "confidence": dietary_conf},
            "weather_conditions": {"value": weather_val, "confidence": weather_conf},
            "accessibility_requirements": {"value": access_val, "confidence": access_conf},
            "safety_preferences": {"value": safety_val, "confidence": safety_conf},
            "crowd_tolerance": {"value": "low" if "avoid crowd" in p else "medium", "confidence": 0.50}
        }
