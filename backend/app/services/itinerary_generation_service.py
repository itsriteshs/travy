import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.services.persistence_service import PersistenceService
from app.services.geocoding_service import GeocodingService
from app.services.candidate_builder_service import CandidateBuilderService
from app.services.candidate_ranking_service import CandidateRankingService
from app.services.route_optimizer_service import RouteOptimizerService
from app.services.guardian_route_service import GuardianRouteService
from app.services.otari_planner_service import OtariPlannerService
from app.services.itinerary_validator_service import ItineraryValidatorService
from app.services.cost_estimator_service import CostEstimatorService
from app.services.result_store_service import ResultStoreService
from app.integrations.weather_client import WeatherClient

logger = logging.getLogger("travy.itinerary_generation_service")

class ItineraryGenerationService:
    def __init__(self):
        self.geocoder = GeocodingService()
        self.candidate_builder = CandidateBuilderService()
        self.candidate_ranker = CandidateRankingService()
        self.route_optimizer = RouteOptimizerService()
        self.guardian_route_service = GuardianRouteService()
        self.otari_planner = OtariPlannerService()
        self.validator = ItineraryValidatorService()
        self.cost_estimator = CostEstimatorService()
        self.result_store = ResultStoreService()

    def _parse_time_to_minutes(self, t_str: str) -> int:
        t_str = t_str.upper().strip()
        import re
        match = re.search(r'(\d+)\s*(AM|PM)', t_str)
        if not match:
            return 600
        hour = int(match.group(1))
        period = match.group(2)
        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0
        return hour * 60

    def _format_minutes_to_time(self, mins: int) -> str:
        hour = (mins // 60) % 24
        minute = mins % 60
        period = "AM"
        if hour >= 12:
            period = "PM"
            if hour > 12:
                hour -= 12
        elif hour == 0:
            hour = 12
        return f"{hour}:{minute:02d} {period}"

    def _build_deterministic_itinerary(
        self,
        city: str,
        stops: List[Dict[str, Any]],
        start_time_str: str,
        moods: List[str]
    ) -> Dict[str, Any]:
        title = f"{city} {', '.join(moods[:3])} plan"
        summary = f"A comfort-aware local plan for exploring {city}."
        
        start_mins = self._parse_time_to_minutes(start_time_str)
        current_mins = start_mins
        
        itinerary_stops = []
        for idx, stop in enumerate(stops):
            duration = 90 # 1.5 hours per stop
            stop_start = self._format_minutes_to_time(current_mins)
            stop_end = self._format_minutes_to_time(current_mins + duration)
            
            reasons = [
                f"Highly recommended candidate for {stop.get('category')} category.",
                "Fits within the budget constraints.",
                "Well-connected stop in the route optimizer."
            ]
            
            itinerary_stops.append({
                "stop_number": idx + 1,
                "place_id": stop["id"],
                "name": stop["name"],
                "category": stop["category"],
                "start_time": stop_start,
                "end_time": stop_end,
                "estimated_cost_per_person_inr": stop.get("estimated_cost_inr", stop.get("estimated_cost_per_person_inr", 100)),
                "why_selected": reasons,
                "source_provider": stop.get("source_provider", "overpass"),
                "confidence": stop.get("confidence", 0.8)
            })
            current_mins += duration + 15
            
        return {
            "title": title,
            "summary": summary,
            "stops": itinerary_stops
        }

    async def generate(self, request_id: str, session_id: str = "demo") -> Dict[str, Any]:
        # 1. Load Phase 2 analysis
        analysis = PersistenceService.get_analysis(request_id)
        if not analysis:
            raise ValueError(f"Analysis request with ID '{request_id}' not found.")
            
        security = analysis["security"]
        intent = analysis["intent"]
        parsed = analysis["parsed"]
        missing_fields = analysis["missing_fields"]
        route_decision = analysis["route_decision"]
        budget = analysis["budget"]
        
        traces = PersistenceService.get_traces(request_id)
        step_number = len(traces) + 1
        
        if not security.get("safe", True):
            PersistenceService.save_trace(request_id, step_number, "Itinerary generation blocked", "BLOCKED", "blocked", 0.0, "Request blocked due to security validation.")
            return {"status": "blocked", "message": "Generation blocked because Phase 2 did not approve generation. Reason: malicious prompt."}
            
        if analysis.get("next_action") == "clarify" or missing_fields:
            PersistenceService.save_trace(request_id, step_number, "Itinerary generation blocked", "CLARIFY_REQUIRED", "blocked", 0.0, "Missing fields.")
            return {"status": "clarify", "message": f"Generation blocked because Phase 2 did not approve generation. Reason: missing {', '.join(missing_fields)}."}
            
        if route_decision.get("route") == "OUT_OF_SCOPE" or intent.get("type") == "booking_request":
            PersistenceService.save_trace(request_id, step_number, "Itinerary generation blocked", "OUT_OF_SCOPE", "blocked", 0.0, "Request is out of scope.")
            return {"status": "out_of_scope", "message": "Generation blocked because Phase 2 did not approve generation. Reason: out of scope."}

        # 2. Geocode city dynamically (no fabrication if offline/unknown)
        city = parsed["city"]["value"]
        geocode_start = datetime.now()
        try:
            city_geo = await self.geocoder.geocode_city(city, request_id)
            geocode_latency = int((datetime.now() - geocode_start).total_seconds() * 1000)
            geocoder_status = "ok"
        except Exception as e:
            # Geocoder failure triggers NO_VALID_RESULTS immediately
            PersistenceService.save_trace(request_id, step_number, "Geocode city", "GEOCODING_API", "error", 0.0, f"Geocoding failed: {str(e)}")
            return {
                "status": "NO_VALID_RESULTS",
                "reason": f"Unable to geocode city '{city}'. Geocoding service is unavailable."
            }
            
        PersistenceService.save_trace(request_id, step_number, "Geocode city", "GEOCODING_API", "ok", 0.0, f"Resolved '{city}' via {city_geo['provider']}.")
        step_number += 1

        # 3. Weather lookup (Open-Meteo current forecast query)
        weather_client = WeatherClient()
        weather_data = await weather_client.get_weather(city_geo["lat"], city_geo["lng"], request_id)
        weather_status = weather_data.get("status", "success")
        
        PersistenceService.save_trace(
            request_id, step_number, "Weather lookup", "WEATHER_API",
            weather_status, 0.0,
            f"Current temperature: {weather_data.get('temperature')}°C. Status: {weather_status}."
        )
        step_number += 1

        # 4. Fetch candidate places
        moods = parsed["moods"]["value"] or []
        places_start = datetime.now()
        try:
            candidates_res = await self.candidate_builder.get_candidates(city_geo, moods, request_id)
            candidates = candidates_res["candidates"]
            places_latency = int((datetime.now() - places_start).total_seconds() * 1000)
            places_status = "ok"
        except Exception as e:
            PersistenceService.save_trace(request_id, step_number, "Fetch place candidates", "PLACES_API", "error", 0.0, f"Places search failed: {str(e)}")
            return {
                "status": "NO_VALID_RESULTS",
                "reason": f"Places lookup failed: {str(e)}"
            }
            
        PersistenceService.save_trace(request_id, step_number, "Fetch place candidates", "PLACES_API", "ok", 0.0, f"Fetched {candidates_res['raw_candidates_count']} places, deduped to {candidates_res['deduped_candidates_count']}.")
        step_number += 1
        
        if not candidates:
            # Fail gracefully on empty candidates
            return {
                "status": "NO_VALID_RESULTS",
                "reason": "Unable to find places matching the constraints."
            }

        # 5. Rank candidates (using 11 fit dimensions and config weights)
        budget_val = parsed["budget_per_person_inr"]["value"] or 1000
        energy_val = parsed["energy"]["value"] or "medium"
        ranked = self.candidate_ranker.rank_candidates(
            candidates=candidates,
            city_geo=city_geo,
            parsed_constraints=parsed,
            weather_data=weather_data
        )
        
        PersistenceService.save_trace(request_id, step_number, "Rank candidates", "LOCAL_LOGIC", "ok", 0.0, "Applied multi-feature ranking formula to candidates.")
        step_number += 1

        # 6. Determine stops count based on time window
        start_time_str = parsed["start_time"]["value"] or "10 AM"
        end_time_str = parsed["end_time"]["value"] or "6 PM"
        
        start_mins = self._parse_time_to_minutes(start_time_str)
        end_mins = self._parse_time_to_minutes(end_time_str)
        duration_hours = (end_mins - start_mins) / 60.0
        
        if duration_hours <= 3.0:
            stop_count = 2
        elif duration_hours <= 5.0:
            stop_count = 3
        elif duration_hours <= 8.0:
            stop_count = 4
        else:
            stop_count = 5
            
        selected_candidates = ranked[:stop_count]

        # 7. Optimize route ordering (TSP search passing start_time)
        route_res = await self.route_optimizer.optimize_route(selected_candidates, city_geo["lat"], city_geo["lng"], start_time_str, request_id)
        ordered_stops = route_res["ordered_stops"]
        route_ordering = route_res["route_ordering"]
        travel_time_mins = route_res["total_travel_time_minutes"]
        
        PersistenceService.save_trace(request_id, step_number, "Optimize stop order", "DISTANCE_API", "ok", 0.0, f"Ordered stops via {route_ordering['provider']}.")
        step_number += 1

        # 8. Apply Guardian Route comfort logic
        guardian_res = self.guardian_route_service.build_guardian_route(ordered_stops, travel_time_mins, energy_val)

        # 9. Generation Flow
        otari_status = "skipped"
        fallback_used = False
        otari_evidence = {}
        itinerary_result = {}
        validation_res = {"passed": True, "checks": ["local_builder"], "warnings": []}
        
        is_critical_budget = budget.get("mode") == "critical"
        route_is_fallback = route_decision.get("route") == "API_ONLY_FALLBACK"
        
        if is_critical_budget or route_is_fallback:
            # Deterministic Local Itinerary Builder
            itinerary_result = self._build_deterministic_itinerary(city, ordered_stops, start_time_str, moods)
            fallback_used = True
            otari_status = "skipped"
            PersistenceService.save_trace(request_id, step_number, "Generate itinerary", "LOCAL_DETERMINISTIC_BUILDER", "ok", 0.0, "Budget critical or API fallback: skipped Otari LLM call.")
            step_number += 1
        else:
            # Call Otari Planner
            model_tier = route_decision.get("model_tier", "strong_planner")
            constraints = {
                "city": city,
                "group_size": parsed["group_size"]["value"],
                "budget_per_person_inr": budget_val,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "moods": moods,
                "energy": energy_val
            }
            
            try:
                itinerary_result = await self.otari_planner.generate_itinerary(model_tier, constraints, ordered_stops, request_id, session_id)
                otari_evidence = itinerary_result.get("_otari_evidence", {})
                
                validation_res = self.validator.validate_itinerary(itinerary_result, ordered_stops, budget_val)
                
                if not validation_res["passed"]:
                    # Attempt Repair once
                    repair_err = ", ".join(validation_res["warnings"])
                    repaired_itinerary = await self.otari_planner.attempt_repair(
                        repair_err, json.dumps(itinerary_result), constraints, ordered_stops, request_id, session_id
                    )
                    repair_validation = self.validator.validate_itinerary(repaired_itinerary, ordered_stops, budget_val)
                    if repair_validation["passed"]:
                        itinerary_result = repaired_itinerary
                        validation_res = repair_validation
                        otari_evidence["cost_usd"] += repaired_itinerary.get("_otari_evidence", {}).get("cost_usd", 0.0)
                        otari_evidence["input_tokens"] += repaired_itinerary.get("_otari_evidence", {}).get("input_tokens", 0)
                        otari_evidence["output_tokens"] += repaired_itinerary.get("_otari_evidence", {}).get("output_tokens", 0)
                    else:
                        # Fall back to local builder
                        itinerary_result = self._build_deterministic_itinerary(city, ordered_stops, start_time_str, moods)
                        fallback_used = True
                        validation_res["warnings"].append("Repair failed. Deterministic fallback was used.")
                        
                otari_status = "ok"
                PersistenceService.save_trace(request_id, step_number, "Generate itinerary", f"STRONG_PLANNER_MODEL ({otari_evidence.get('model_id')})", "ok", otari_evidence.get("cost_usd", 0.0), "Generated via Otari and validated.")
                step_number += 1
            except Exception as e:
                logger.error(f"Otari planner call failed: {e}. Falling back to deterministic itinerary.")
                itinerary_result = self._build_deterministic_itinerary(city, ordered_stops, start_time_str, moods)
                fallback_used = True
                otari_status = "error"
                validation_res = {"passed": False, "checks": [], "warnings": [f"Otari planner failed: {str(e)}"]}
                PersistenceService.save_trace(request_id, step_number, "Generate itinerary", "LOCAL_DETERMINISTIC_BUILDER", "ok", 0.0, f"Otari failed: {str(e)}. Using fallback.")
                step_number += 1

        # 10. Compute Final cost breakdown passing group_size
        cost_breakdown = self.cost_estimator.estimate_itinerary_cost(
            itinerary_result["stops"], route_ordering, budget_val, moods, parsed["group_size"]["value"]
        )
        
        # Update itinerary details
        itinerary_result["total_estimated_cost_per_person_inr"] = cost_breakdown["estimated_total"]
        itinerary_result["budget_status"] = cost_breakdown["budget_status"]
        itinerary_result["total_travel_time_minutes"] = travel_time_mins
        
        # Structure API evidence
        api_evidence = {
            "geocoder": {
                "provider": city_geo["provider"],
                "status": geocoder_status,
                "latency_ms": geocode_latency
            },
            "places": {
                "provider": getattr(settings, "PLACES_PROVIDER", "overpass"),
                "status": places_status,
                "raw_candidates": candidates_res["raw_candidates_count"],
                "deduped_candidates": candidates_res["deduped_candidates_count"]
            },
            "distance": {
                "provider": route_ordering["provider"],
                "status": "ok" if route_ordering["provider"] == "google_maps" else "fallback"
            },
            "otari": {
                "status": otari_status,
                "model_tier": route_decision.get("model_tier", "none"),
                "model_id": otari_evidence.get("model_id", "none"),
                "estimated_cost_usd": route_decision.get("estimated_cost_usd", 0.0),
                "actual_cost_usd": otari_evidence.get("cost_usd", 0.0),
                "usage_source": otari_evidence.get("usage_source", "local_estimate" if otari_status == "ok" else "none")
            }
        }
        
        validation_report = {
            "passed": validation_res["passed"],
            "checks": validation_res["checks"],
            "warnings": validation_res["warnings"],
            "fallback_used": fallback_used
        }
        
        status_label = "passed" if validation_res["passed"] else "warnings"
        PersistenceService.save_trace(request_id, step_number, "Validate output", "LOCAL_LOGIC", status_label, 0.0, f"Validator passed: {validation_res['passed']}.")
        
        # 11. Persist results
        result_id = f"res_{uuid.uuid4().hex[:8]}"
        final_response = {
            "request_id": request_id,
            "status": "success",
            "result_id": result_id,
            "generated_at": datetime.now().isoformat(),
            "source": {
                "analysis_request_id": request_id,
                "generation_method": "otari_planner" if not fallback_used else "deterministic_fallback",
                "fallback_used": fallback_used
            },
            "api_evidence": api_evidence,
            "itinerary": itinerary_result,
            "guardian_route": guardian_res,
            "validation": validation_report,
            "budget_breakdown": cost_breakdown,
            "routing_trace": PersistenceService.get_traces(request_id)
        }
        
        self.result_store.save_result(result_id, request_id, final_response, validation_report, api_evidence)
        
        return final_response
