# In-memory trace persistence store
_trace_store = {}

class TraceService:
    def save_trace(self, request_id: str, trace_data: list):
        _trace_store[request_id] = trace_data
        
    def get_trace(self, request_id: str) -> list:
        return _trace_store.get(request_id, [])

    def build_trace(self, security: dict, intent: dict, parsed: dict, complexity: dict, budget: dict, route_decision: dict) -> list:
        trace = []
        
        # Step 1: Security Scan
        trace.append({
            "step": 1,
            "task": "Prompt injection scan",
            "route": "LOCAL_LOGIC",
            "cost_usd": 0.0,
            "status": "safe" if security["safe"] else "blocked",
            "reason": "No suspicious instruction detected." if security["safe"] else f"Suspicious phrases detected: {security['detected']}"
        })
        
        # Step 2: Intent Classification
        trace.append({
            "step": 2,
            "task": "Intent classification",
            "route": "LOCAL_LOGIC",
            "cost_usd": 0.0,
            "status": intent["type"],
            "reason": intent["reason"]
        })
        
        if not security["safe"]:
            return trace
            
        # Step 3: Constraint Parsing
        overall_conf = 0.9 if parsed.get("city", {}).get("value") else 0.4
        trace.append({
            "step": 3,
            "task": "Constraint parsing",
            "route": "LOCAL_PARSER",
            "cost_usd": 0.0,
            "status": "high_confidence" if overall_conf >= 0.8 else "low_confidence",
            "reason": "Required fields extracted locally." if overall_conf >= 0.8 else "Vague or missing planning constraints."
        })
        
        # Step 4: Context Selection
        context_mode = "full_context" if budget["mode"] == "healthy" else ("low_budget" if budget["mode"] == "low" else "critical_budget")
        if budget["mode"] == "critical":
            context_mode = "api_only_fallback"
        trace.append({
            "step": 4,
            "task": "Context selection",
            "route": "LOCAL_LOGIC",
            "cost_usd": 0.0,
            "status": context_mode,
            "reason": f"Budget mode is {budget['mode']}."
        })
        
        # Step 5: Model Route Selection
        trace.append({
            "step": 5,
            "task": "Model route selection",
            "route": route_decision["route"],
            "cost_usd": route_decision["estimated_cost_usd"],
            "status": "selected_for_phase_3" if route_decision["route"] in ["STRONG_PLANNER_MODEL", "BALANCED_PLANNER_MODEL", "COMPRESSED_CHEAP_MODEL", "LOCAL_LLM"] else "fallback_or_blocked",
            "reason": route_decision["reason"]
        })
        
        return trace
