# Travy Mozilla.ai Integration Handoff

Created: 2026-06-28

## Objective

Integrate the Mozilla.ai stack into `D:\travy` so Travy behaves like a real Otari submission:

- Encoderfile for local embeddings / semantic injection similarity.
- Llamafile for local control-plane decisions.
- mcpd for MCP tool orchestration.
- any-agent for optional MCP-backed agent orchestration.
- Otari only for final itinerary generation.

No mock locations, fallback itineraries, fake scores, random generation, or synthetic travel data should be used in the production planning path.

## Key Security Note

The Otari API key was written to local `.env` only. It was not hardcoded into source files or `.env.example`.

## Files Added

- `.mcpd.toml`
- `HANDOFF.md`
- `backend/app/integrations/llamafile_client.py`
- `backend/app/integrations/encoderfile_client.py`
- `backend/app/integrations/mcpd_client.py`
- `backend/app/services/local_security_service.py`
- `backend/app/services/local_router_service.py`
- `backend/app/services/any_agent_orchestrator_service.py`

## Files Modified

- `backend/app/core/config.py`
- `backend/app/api/planner.py`
- `backend/app/services/router_engine.py`
- `backend/app/services/budget_ledger_service.py`
- `backend/app/services/candidate_builder_service.py`
- `backend/app/services/itinerary_generation_service.py`
- `backend/app/integrations/weather_client.py`
- `backend/app/integrations/otari_client.py`
- `backend/requirements.txt`
- `.env.example`
- `.env` local only

## Current Behavior

Security:

- `/api/planner/analyze` now uses `LocalSecurityService`.
- It first tries llamafile structured JSON.
- If llamafile is unavailable, it falls back to encoderfile similarity plus lexical fail-closed rules.
- Blocked prompts never reach Otari.

Routing:

- Router now estimates cost from `config/model-pricing.json`.
- Final travel planning routes to Otari when budget allows.
- Local model is reserved for classification, extraction, security, routing, and budget decisions.
- Budget-exceeded requests do not produce local fallback itineraries.

Budget:

- Budget ledger no longer forces demo low/critical values.
- It reads recorded spend and `DAILY_BUDGET_USD`.
- `auto` mode maps remaining budget ratio to healthy/low/critical.

Generation:

- Weather lookup no longer fabricates default clear weather on failure.
- Missing moods no longer generate default categories.
- Otari timeout increased to `OTARI_TIMEOUT_SECONDS`, default `900`.
- If Otari fails, response is `OTARI_UNAVAILABLE`; no deterministic itinerary fallback.
- If Otari repair fails validation, response is `OTARI_VALIDATION_FAILED`; no fake itinerary.
- Successful responses include `usage_transparency`.

## Verification Completed

From `D:\travy`:

```powershell
.\backend\.venv\Scripts\python.exe -m compileall -q backend\app
```

Passed.

Focused tests:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest -q backend\app\tests\test_health.py backend\app\tests\test_otari_client_mock.py
```

Passed: `7 passed`.

Local smoke check:

```powershell
cd D:\travy\backend
@'
import asyncio
from app.services.local_security_service import LocalSecurityService
from app.services.local_router_service import LocalRouterService

async def main():
    sec = await LocalSecurityService().scan(
        'Plan Delhi for 2 friends from 2 PM to 8 PM. Budget rs 800 each, food and photos.'
    )
    print({'safe': sec['safe'], 'risk_score': sec['risk_score'], 'scanner': sec.get('scanner')})
    router = LocalRouterService()
    features = router.estimate_features(
        prompt='Plan Delhi for 2 friends from 2 PM to 8 PM. Budget rs 800 each, food and photos.',
        security=sec,
        intent={'type': 'travel_planning'},
        parsed={'city': {'value': 'Delhi'}, 'moods': {'value': ['food', 'photos']}},
        complexity={'score': 60},
        budget={'remaining_budget_usd': 2.0},
        missing_fields=[],
        estimated_cost_usd=0.01,
    )
    print(await router.decide(features))
asyncio.run(main())
'@ | .\.venv\Scripts\python.exe -
```

Result:

- Security safe.
- Router selected `OTARI`.
- Llamafile and encoderfile were unavailable locally, so the deterministic safety net was used.

## Known Blockers

1. Llamafile server is not running.

Expected:

```powershell
.\your-model.llamafile.exe --server --host 127.0.0.1 --port 8081
```

2. Encoderfile server is not running.

Expected:

```powershell
.\build\travy-semantic-embedder.encoderfile.exe serve --http-port 8082 --disable-grpc
```

3. `.mcpd.toml` references `uvx::travy-mcp-server`, but that MCP server package does not appear to exist in this repo yet.

Need either:

- implement `travy-mcp-server`, or
- change `.mcpd.toml` to point at an actual MCP server command/package.

4. The full legacy backend test suite timed out after 124 seconds.

Likely cause:

- existing tests still assume demo-era behavior such as deterministic fallback generation, mocked live APIs, and Otari fallback.

Run focused tests first, then update old tests to match the stricter no-fabrication behavior.

## Run Commands

Backend:

```powershell
cd D:\travy\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

Frontend:

```powershell
cd D:\travy
npm run dev
```

Open:

```text
http://localhost:3000/planner
```

## Suggested Next Steps

1. Start or install a small llamafile model on port `8081`.
2. Build or download an encoderfile embedder and run it on port `8082`.
3. Implement the real `travy-mcp-server` MCP server exposing:
   - `maps.search_places`
   - `maps.route`
   - `weather.lookup`
   - `budget.calculate`
   - `travel.score_candidates`
   - `otari.generate_plan`
4. Update frontend labels that still say demo/fallback.
5. Update legacy tests that expect deterministic fallback itineraries.
6. Run an end-to-end live request through `/api/planner/analyze` and `/api/planner/generate`.

## Important Philosophy

The current source now favors honest failure over impressive fake success:

- no weather fabrication,
- no generated default categories,
- no local itinerary fallback,
- no Otari prompt reaching final generation after a blocked security scan,
- no final itinerary if no real candidates exist.

