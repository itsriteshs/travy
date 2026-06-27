# Travy — Complete Project Documentation

> **Cost-aware social travel planning assistant** powered by real-time geospatial APIs, dynamic multi-dimension scoring, and LLM-based itinerary generation.

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Complete Project Structure](#complete-project-structure)
4. [Environment Variables](#environment-variables)
5. [Configuration Files](#configuration-files)
6. [Backend Architecture](#backend-architecture)
7. [API Endpoints](#api-endpoints)
8. [Frontend Architecture](#frontend-architecture)
9. [Request Processing Pipeline](#request-processing-pipeline)
10. [Scoring & Ranking Engine](#scoring--ranking-engine)
11. [Route Optimization (TSP)](#route-optimization-tsp)
12. [LLM Integration (Otari)](#llm-integration-otari)
13. [Budget System](#budget-system)
14. [Security Layer](#security-layer)
15. [Guardian Route System](#guardian-route-system)
16. [Database & Persistence](#database--persistence)
17. [Testing](#testing)
18. [How to Run](#how-to-run)
19. [Design Principles](#design-principles)

---

## Overview

Travy is a full-stack travel planning application that takes a natural-language prompt (e.g. *"Plan Delhi for 4 friends from 2 PM to 8 PM, budget ₹800 each, shopping, food, photos"*) and produces a realistic, optimized, explainable itinerary using only real places and real data.

**Key properties:**
- **Zero-mock**: No fabricated locations, prices, ratings, or travel times. If real data cannot be found, the system fails gracefully with `{"status": "NO_VALID_RESULTS", "reason": "..."}`.
- **Cost-aware AI routing**: An internal budget ledger tracks LLM API spend and dynamically routes requests to cheaper or local-only pipelines as funds deplete.
- **11-dimension candidate scoring**: Every candidate venue is scored across budget fit, distance fit, time fit, weather fit, group fit, mood fit, opening hours fit, safety fit, crowd fit, fatigue penalty, and transport fit — all with configurable weights.
- **Constraint-aware TSP routing**: Stop ordering factors in travel time, meal timing (lunch/dinner windows), opening hours, and fatigue accumulation.

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | ^15.1.0 | React framework, SSR, file-based routing |
| React | ^19.0.0 | UI library |
| TypeScript | ^5.7.2 | Type safety |
| TailwindCSS | ^3.4.17 | Utility-first CSS |
| Lucide React | ^0.468.0 | Icon library |
| clsx + tailwind-merge | latest | Conditional class merging |
| Playwright | ^1.61.1 | E2E browser testing |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Runtime |
| FastAPI | >=0.110.0 | API framework |
| Uvicorn | >=0.28.0 | ASGI server |
| Pydantic | >=2.6.0 | Request/response validation |
| httpx | >=0.27.0 | Async HTTP client |
| python-dotenv | >=1.0.1 | Environment variable loading |
| SQLite | built-in | Persistence (traces, results, analyses) |
| pytest | >=8.0.0 | Unit testing |
| pytest-asyncio | >=0.23.0 | Async test support |

### External APIs (No Keys Required)
| Service | URL | Purpose |
|---|---|---|
| Nominatim (OSM) | nominatim.openstreetmap.org | City geocoding (lat/lng resolution) |
| Overpass (OSM) | overpass-api.de | Real place search (restaurants, monuments, parks, etc.) |
| Open-Meteo | api.open-meteo.com | Current weather conditions (temperature, humidity, weather code) |

### External APIs (Optional, Key Required)
| Service | Env Var | Purpose |
|---|---|---|
| Google Places | `GOOGLE_PLACES_API_KEY` | Premium place search |
| Foursquare | `FOURSQUARE_API_KEY` | Venue discovery |
| Mapbox | `MAPBOX_ACCESS_TOKEN` | Geocoding & routing |
| Otari | `OTARI_API_KEY` | LLM inference gateway (Gemma, Qwen, Llama) |

---

## Complete Project Structure

```
d:\travy\
│
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore rules
├── README.md                     # Original readme
├── design.md                     # Design specification document (33 KB)
├── package.json                  # Frontend dependencies & scripts
├── package-lock.json             # Lockfile
├── tsconfig.json                 # TypeScript configuration
├── next.config.ts                # Next.js configuration
├── next-env.d.ts                 # Next.js type declarations
├── tailwind.config.ts            # TailwindCSS configuration
├── postcss.config.mjs            # PostCSS configuration
├── eslint.config.mjs             # ESLint configuration
├── travy.db                      # Root-level SQLite database
│
├── config/                       # Shared configuration files
│   ├── model-pricing.json        # LLM token pricing (per-model input/output costs)
│   ├── runtime-config.json       # Budget thresholds, security weights, retry config
│   └── weights.json              # Candidate ranking weights (11 fit dimensions)
│
├── app/                          # Next.js App Router pages
│   ├── layout.tsx                # Root layout (fonts, metadata, shell)
│   ├── page.tsx                  # Landing page (/)
│   ├── globals.css               # Global CSS styles
│   ├── planner/
│   │   └── page.tsx              # Planner page (/planner) — main user interface
│   ├── results/
│   │   └── page.tsx              # Results page (/results) — itinerary display
│   ├── demo/
│   │   └── page.tsx              # Demo page (/demo) — scenario runner
│   ├── ai-router/
│   │   └── page.tsx              # AI Router dashboard (/ai-router)
│   └── security/
│       └── page.tsx              # Security scanner page (/security)
│
├── components/                   # React components
│   ├── layout/
│   │   ├── app-shell.tsx         # App shell wrapper
│   │   └── neo-navbar.tsx        # Navigation bar
│   ├── ui/                       # Reusable UI primitives (Neo design system)
│   │   ├── neo-badge.tsx         # Badge component
│   │   ├── neo-button.tsx        # Button component
│   │   ├── neo-card.tsx          # Card component
│   │   ├── neo-input.tsx         # Input component
│   │   ├── neo-progress.tsx      # Progress bar component
│   │   └── neo-textarea.tsx      # Textarea component
│   └── travy/                    # Domain-specific components
│       ├── budget-meter.tsx      # Budget visualization meter
│       ├── context-priority-table.tsx  # Context priority display
│       ├── demo-action-card.tsx  # Demo scenario action card
│       ├── fit-score-card.tsx    # Fit score display card
│       ├── guardian-route-card.tsx # Guardian route comparison card
│       ├── itinerary-timeline.tsx # Itinerary stops timeline
│       ├── pipeline-trace.tsx    # Pipeline execution trace
│       └── routing-table.tsx     # Routing decision table
│
├── lib/                          # Shared libraries
│   ├── utils.ts                  # General utilities (cn helper)
│   ├── styles/
│   │   └── neo.ts                # Neo design system style tokens
│   ├── server/
│   │   └── utils/
│   │       └── config.ts         # Server-side configuration
│   └── travy/                    # Travy domain logic
│       ├── types.ts              # TypeScript type definitions (all backend response shapes)
│       ├── backend-api.ts        # Backend API client (fetch wrappers)
│       ├── demo-data.ts          # Demo scenario data
│       ├── demo-logic.ts         # Demo orchestration logic
│       └── storage.ts            # Client-side storage utilities
│
├── tests/                        # Frontend tests
│   └── budget-service.test.ts    # Budget service tests
│
└── backend/                      # Python FastAPI backend
    ├── requirements.txt          # Python dependencies
    ├── travy.db                  # Backend SQLite database
    ├── .venv/                    # Python virtual environment (gitignored)
    │
    └── app/
        ├── __init__.py           # Package init
        ├── main.py               # FastAPI app entry point, CORS, router registration
        │
        ├── core/                 # Core configuration
        │   ├── config.py         # Settings class (env vars, model validation, weights loader)
        │   └── demo_state.py     # Demo mode state tracker
        │
        ├── api/                  # API route handlers
        │   ├── health.py         # GET /health, GET /ready
        │   ├── ai_smoke.py       # GET /api/ai/smoke, GET /api/ai/models
        │   ├── security.py       # POST /api/security/scan
        │   ├── planner.py        # POST /api/planner/analyze, POST /api/planner/generate,
        │   │                     #   GET /api/planner/trace/{id}, GET /api/results/{id}
        │   ├── integrations.py   # GET /api/integrations/health, GET /api/integrations/otari,
        │   │                     #   GET /api/router/live-usage
        │   └── demo.py           # GET /api/demo/status, POST /api/demo/reset,
        │                         #   POST /api/demo/run-scenario,
        │                         #   GET /api/sessions/{id}/requests,
        │                         #   GET /api/sessions/{id}/results,
        │                         #   GET /api/debug/api-calls/{id}
        │
        ├── integrations/         # External API clients
        │   ├── base_client.py    # Base HTTP client (retries, logging, error handling)
        │   ├── geocoder_client.py # Nominatim geocoder (city → lat/lng)
        │   ├── places_client.py  # Overpass API place search (restaurants, monuments, etc.)
        │   ├── distance_client.py # Distance matrix client (Google Maps or Haversine fallback)
        │   ├── weather_client.py # Open-Meteo weather client (temperature, humidity, code)
        │   └── otari_client.py   # Otari LLM API client (completions, token tracking)
        │
        ├── services/             # Business logic services
        │   ├── parser_service.py             # Regex constraint extractor (14 parameters)
        │   ├── otari_extractor_service.py    # LLM-based constraint extractor (backup)
        │   ├── injection_service.py          # Prompt injection scanner
        │   ├── intent_classifier_service.py  # Intent classifier (travel_plan, booking, etc.)
        │   ├── complexity_service.py         # Request complexity scorer
        │   ├── context_service.py            # Context priority selector (budget-aware)
        │   ├── budget_service.py             # Budget mode resolver
        │   ├── budget_ledger_service.py      # AI spend ledger (USD tracking)
        │   ├── router_engine.py              # Model routing decision engine
        │   ├── geocoding_service.py          # Geocoding service wrapper
        │   ├── place_provider_service.py     # Place provider service wrapper
        │   ├── candidate_builder_service.py  # Candidate collection & deduplication
        │   ├── candidate_ranking_service.py  # 11-dimension candidate scoring engine
        │   ├── route_optimizer_service.py    # TSP route optimizer (meal timing, fatigue)
        │   ├── guardian_route_service.py      # Guardian Route comfort logic
        │   ├── otari_planner_service.py      # LLM itinerary generation + repair
        │   ├── itinerary_validator_service.py # Output validation (place ID checks)
        │   ├── cost_estimator_service.py     # Budget breakdown calculator
        │   ├── itinerary_generation_service.py # Main orchestrator (end-to-end pipeline)
        │   ├── persistence_service.py        # SQLite persistence (analyses, traces, results)
        │   ├── result_store_service.py       # Result storage wrapper
        │   ├── trace_service.py              # Trace logging service
        │   ├── otari_usage_service.py        # Otari usage tracker
        │   ├── otari_client.py               # Re-export of integrations.otari_client
        │   ├── integration_health_service.py # Integration health checker
        │   ├── demo_orchestrator_service.py  # Demo scenario orchestrator
        │   ├── error_response_service.py     # Error response builder
        │   └── api_call_logger_service.py    # API call logger
        │
        └── tests/                # Backend unit tests
            ├── __init__.py
            ├── test_health.py              # Health endpoint tests (2 tests)
            ├── test_otari_client_mock.py   # Otari client mock tests (5 tests)
            ├── test_phase2.py             # Phase 2 analysis tests (16 tests)
            └── test_phase3_phase4.py      # Phase 3-4 generation tests (8 tests)
```

---

## Environment Variables

File: `.env` (copy from `.env.example`)

```env
# Otari LLM Gateway
OTARI_BASE_URL=https://api.otari.ai/v1
OTARI_API_KEY=tk_placeholder              # Your Otari API key
OTARI_MODE=connected                       # connected | local

# Model Configuration (provider:model_name format)
OTARI_LOCAL_LLM_MODEL=mzai:google/gemma-3-27b-it
OTARI_CHEAP_MODEL=mzai:google/gemma-3-27b-it
OTARI_BALANCED_MODEL=mzai:Qwen/Qwen3-32B
OTARI_STRONG_MODEL=mzai:meta-llama/Llama-3.3-70B-Instruct

# Database
DATABASE_URL=sqlite:///./travy.db

# URLs
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080

# Optional External APIs (leave blank to use free OSM/Open-Meteo)
GOOGLE_PLACES_API_KEY=
FOURSQUARE_API_KEY=
MAPBOX_ACCESS_TOKEN=
WEATHER_API_KEY=
```

---

## Configuration Files

### `config/model-pricing.json`
Defines per-token pricing for each supported LLM model. Used by the budget ledger to estimate and track AI spend.

```json
{
  "gemma-3-27b-it": {
    "input_token_price": 0.0000003,
    "output_token_price": 0.000001
  },
  "qwen-2.5-32b": {
    "input_token_price": 0.0000005,
    "output_token_price": 0.0000015
  },
  "llama-3.3-70b": {
    "input_token_price": 0.0000008,
    "output_token_price": 0.000003
  }
}
```

### `config/runtime-config.json`
Runtime parameters for budget thresholds, security scanning weights, and retry policy.

```json
{
  "budget": {
    "defaultTotalUsd": 2.0,
    "modeThresholds": {
      "healthy": 0.60,
      "cautious": 0.35,
      "low": 0.15,
      "critical": 0.05
    }
  },
  "security": {
    "riskThreshold": 70,
    "weights": {
      "roleEscalation": 30,
      "instructionOverride": 25,
      "promptExtraction": 25,
      "jailbreakPattern": 20
    }
  },
  "retry": {
    "otariMaxAttempts": 2,
    "otariTimeoutMs": 30000
  }
}
```

### `config/weights.json`
Controls the 11 fit dimensions used for candidate venue scoring. Weights sum to 1.0. Modify these to change how venues are prioritized without touching code.

```json
{
    "budget_fit": 0.15,
    "distance_fit": 0.10,
    "time_fit": 0.10,
    "weather_fit": 0.10,
    "group_fit": 0.10,
    "mood_fit": 0.15,
    "opening_hours_fit": 0.10,
    "safety_fit": 0.10,
    "crowd_fit": 0.05,
    "fatigue_penalty": 0.05,
    "transport_fit": 0.05
}
```

---

## Backend Architecture

The backend follows a layered service architecture:

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│  planner.py │ health.py │ demo.py │ security.py │ ...   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   Service Layer                         │
│  parser_service │ candidate_ranking │ route_optimizer   │
│  itinerary_generation │ cost_estimator │ router_engine  │
│  guardian_route │ injection_service │ complexity_service │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                Integration Layer                        │
│  geocoder_client │ places_client │ distance_client      │
│  weather_client  │ otari_client  │ base_client          │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│               Persistence Layer                         │
│  persistence_service (SQLite) │ result_store_service    │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Health & Diagnostics
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok"}` |
| GET | `/ready` | Returns `{"status": "ready"}` |
| GET | `/api/ai/smoke` | Smoke test: sends a ping to the Otari LLM API |
| GET | `/api/ai/models` | Returns configured model IDs for all tiers |

### Planner (Core)
| Method | Path | Description |
|---|---|---|
| POST | `/api/planner/analyze` | Analyzes a natural-language prompt. Extracts constraints, classifies intent, scans for injection, decides model route. Returns `request_id` and `next_action`. |
| POST | `/api/planner/generate` | Takes `request_id` from analyze. Geocodes city, fetches real places, ranks candidates, optimizes route, generates itinerary (via LLM or deterministic builder). Returns full itinerary with evidence. |
| GET | `/api/planner/trace/{request_id}` | Returns the execution trace for a request. |
| GET | `/api/results/{request_id}` | Retrieves stored generation results. |

### Security
| Method | Path | Description |
|---|---|---|
| POST | `/api/security/scan` | Scans text for prompt injection patterns. Returns risk score and detected patterns. |

### Integrations
| Method | Path | Description |
|---|---|---|
| GET | `/api/integrations/health` | Health check for all external services (DB, Otari, geocoder, places, distance). |
| GET | `/api/integrations/otari` | Direct Otari connectivity check. |
| GET | `/api/router/live-usage` | Returns current AI budget usage stats. |

### Demo
| Method | Path | Description |
|---|---|---|
| GET | `/api/demo/status` | Returns current demo mode, request count, cost. |
| POST | `/api/demo/reset` | Resets demo state and DB logs. |
| POST | `/api/demo/run-scenario` | Runs a predefined scenario (e.g. `valid_delhi`, `prompt_injection`). |
| GET | `/api/sessions/{id}/requests` | Returns all requests for a session. |
| GET | `/api/sessions/{id}/results` | Returns all results for a session. |
| GET | `/api/debug/api-calls/{id}` | Returns API call logs for a request. |

---

## Frontend Architecture

### Pages (Next.js App Router)
| Route | File | Description |
|---|---|---|
| `/` | `app/page.tsx` | Landing page with project overview |
| `/planner` | `app/planner/page.tsx` | Main planner UI: prompt input → analyze → generate → display itinerary |
| `/results` | `app/results/page.tsx` | Results viewer with itinerary timeline, budget breakdown, guardian route |
| `/demo` | `app/demo/page.tsx` | Demo scenario runner with predefined test cases |
| `/ai-router` | `app/ai-router/page.tsx` | AI router dashboard showing model routing decisions and budget usage |
| `/security` | `app/security/page.tsx` | Security scanner UI for testing prompt injection detection |

### Component Library
The frontend uses a custom **Neo design system** with reusable primitives:
- `neo-button.tsx`, `neo-card.tsx`, `neo-input.tsx`, `neo-textarea.tsx`, `neo-badge.tsx`, `neo-progress.tsx`

Domain components under `components/travy/` handle visualization of backend data:
- `itinerary-timeline.tsx` — Renders ordered stops with times, costs, and fit scores
- `budget-meter.tsx` — Visual AI budget gauge
- `guardian-route-card.tsx` — Compares fastest vs. comfort-aware routes
- `fit-score-card.tsx` — Displays multi-dimension fit breakdown per stop
- `routing-table.tsx` — Shows execution trace steps
- `pipeline-trace.tsx` — Renders pipeline step indicators
- `context-priority-table.tsx` — Shows what context was included/dropped

### Backend API Client
`lib/travy/backend-api.ts` provides typed fetch wrappers:
- `analyzePlanner(prompt, budgetMode)` → `BackendAnalysis`
- `generatePlanner(requestId)` → `BackendGeneration`
- `scanSecurityText(text)` → `SecurityScanResult`
- `getIntegrationHealth()` → `BackendHealth`
- `runDemoScenario(scenario)` → scenario result
- Helper functions: `parsedFromBackend()`, `budgetFromAnalysis()`, `stopsFromGeneration()`, `guardianFromGeneration()`, `planFitScore()`

### TypeScript Types
All backend response shapes are defined in `lib/travy/types.ts`:
- `BackendAnalysis`, `BackendGeneration`, `BackendHealth`, `BackendUsage`
- `ParsedTravelRequest`, `InjectionScanResult`, `RouteDecision`, `BudgetState`
- `ItineraryStop`, `GuardianRoute`, `BudgetBreakdown`, `ContextSelection`

---

## Request Processing Pipeline

The planner operates in two phases:

### Phase 1: Analyze (`POST /api/planner/analyze`)

```
User Prompt
    │
    ▼
1. Prompt Injection Scan (injection_service.py)
    │ → Blocked if risk_score > threshold
    ▼
2. Intent Classification (intent_classifier_service.py)
    │ → travel_plan | booking_request | budget_math | ...
    ▼
3. Constraint Extraction — 14 Parameters (parser_service.py)
    │ → city, current_location, group_size, budget_per_person_inr,
    │   start_time, end_time, moods, energy, transport,
    │   dietary_restrictions, weather_conditions,
    │   accessibility_requirements, safety_preferences, crowd_tolerance
    ▼
4. Optional LLM Extractor (otari_extractor_service.py)
    │ → Fills gaps the regex parser missed
    ▼
5. Complexity Scoring (complexity_service.py)
    ▼
6. Budget Ledger Check (budget_ledger_service.py)
    ▼
7. Context Selection (context_service.py)
    ▼
8. Model Route Decision (router_engine.py)
    │ → BLOCKED | CLARIFY_REQUIRED | API_ONLY_FALLBACK |
    │   LOCAL_LLM | BALANCED_PLANNER_MODEL | STRONG_PLANNER_MODEL
    ▼
9. Persist Analysis → Return { request_id, next_action }
```

### Phase 2: Generate (`POST /api/planner/generate`)

```
request_id
    │
    ▼
1. Load Analysis (re-check security, missing fields, scope)
    ▼
2. Geocode City → Nominatim API (geocoder_client.py)
    │ → Fail with NO_VALID_RESULTS if geocoding fails
    ▼
3. Weather Lookup → Open-Meteo API (weather_client.py)
    ▼
4. Fetch Candidate Places → Overpass API (places_client.py)
    │ → Fail with NO_VALID_RESULTS if zero candidates
    ▼
5. Rank Candidates → 11-Dimension Scoring (candidate_ranking_service.py)
    ▼
6. Select Top N Stops (based on time window duration)
    ▼
7. Optimize Route Order → Constraint-Aware TSP (route_optimizer_service.py)
    ▼
8. Guardian Route Comfort Logic (guardian_route_service.py)
    ▼
9. Generate Itinerary
    │ ├─ LLM Path: otari_planner_service.py (if budget allows)
    │ └─ Deterministic Path: _build_deterministic_itinerary (if critical budget)
    ▼
10. Validate Output (itinerary_validator_service.py)
    │ → Repair via LLM if validation fails, then fallback to deterministic
    ▼
11. Cost Breakdown (cost_estimator_service.py)
    ▼
12. Persist & Return Full Response
```

---

## Scoring & Ranking Engine

Every candidate place is scored across **11 fit dimensions** with configurable weights from `config/weights.json`:

| Dimension | Weight | Formula |
|---|---|---|
| **budget_fit** | 0.15 | Sigmoid decay: `100 / (1 + e^(cost_diff / (budget * 0.25)))` |
| **distance_fit** | 0.10 | Linear decay: `100 - dist_km * 7.5` |
| **time_fit** | 0.10 | Ratio match: `100 - abs((90/duration) - 0.25) * 100` |
| **weather_fit** | 0.10 | Comfort index: penalizes outdoor venues in rain/extreme temps |
| **group_fit** | 0.10 | Capacity match: cafes penalized for large groups |
| **mood_fit** | 0.15 | Category overlap: `(matches / total_moods) * 100` |
| **opening_hours_fit** | 0.10 | Binary: 95 if open, 20 if closed |
| **safety_fit** | 0.10 | Rating proxy: `80 + rating * multiplier` |
| **crowd_fit** | 0.05 | Log-based: `100 - log(review_count) * 12` for low tolerance |
| **fatigue_penalty** | 0.05 | Subtracted: penalizes high-energy stops at low-energy pace |
| **transport_fit** | 0.05 | Distance decay: steeper for walking (`* 25`) vs. cab (`* 4`) |

**Final score** = Σ(dimension × weight) − (fatigue_penalty × weight)

---

## Route Optimization (TSP)

The route optimizer uses a constraint-aware nearest-neighbor heuristic:

1. **Distance matrix**: Fetched from Google Maps Distance Matrix API (if key configured) or computed via Haversine formula.
2. **Meal timing**: Restaurants/cafes are prioritized during lunch (12–2 PM) and dinner (7–9 PM) windows with a +50 score bonus.
3. **Fatigue management**: After cumulative fatigue exceeds 60%, rest stops (cafes, restaurants) get +30 bonus; high-energy stops get −20 penalty.
4. **Fatigue accumulation**: Active stops (markets, monuments) add +25 fatigue; rest stops subtract −20 fatigue. Range: [10, 100].

---

## LLM Integration (Otari)

### Model Tiers
| Tier | Model | Use Case | Est. Cost |
|---|---|---|---|
| Local/Cheap | `gemma-3-27b-it` | Constraint extraction, JSON repair | $0.000 |
| Balanced | `Qwen/Qwen3-32B` | Medium-complexity itinerary generation | $0.015 |
| Strong | `Llama-3.3-70B-Instruct` | Complex multi-constraint planning | $0.041 |

### LLM Rules (Phase 10)
LLMs are **only** used to:
- Extract intent and structured constraints from prompts
- Summarize and explain itinerary decisions
- Generate human-readable `why_selected` explanations

LLMs **never** generate:
- Locations, coordinates, prices, travel times, opening hours, ratings, weather data, or routes

### Repair Flow
If the LLM output fails validation (e.g. invented place IDs):
1. Attempt one repair call using the cheap model
2. If repair also fails validation → fall back to deterministic local builder
3. Mark `fallback_used: true` in the response

---

## Budget System

### AI Budget Ledger
The system tracks a global AI spend budget (default $2.00 USD). As requests consume LLM tokens, the budget depletes and the routing engine adapts:

| Budget Mode | Threshold | Behavior |
|---|---|---|
| `healthy` | > 60% remaining | Full model access (strong planner) |
| `cautious` | 35–60% remaining | Balanced model preferred |
| `low` | 15–35% remaining | Cheap model with compressed context |
| `critical` | < 5% remaining | No LLM calls; deterministic-only pipeline |

### Travel Budget Calculator
The cost estimator computes per-person and group totals:
- **Food costs**: Summed from food-category stops
- **Travel costs**: ₹15/km × total route distance
- **Shopping buffer**: ₹300 if shopping mood, ₹50 otherwise
- **Activity/ticket costs**: Non-food, non-shopping stop costs
- **Miscellaneous**: ₹50 baseline

---

## Security Layer

### Prompt Injection Scanner
`injection_service.py` scans prompts for malicious patterns using weighted categories:

| Category | Weight | Examples |
|---|---|---|
| Role Escalation | 30 | "you are now", "act as", "pretend to be" |
| Instruction Override | 25 | "ignore previous", "forget your", "disregard" |
| Prompt Extraction | 25 | "reveal your", "show me your prompt", "system message" |
| Jailbreak Pattern | 20 | "DAN mode", "developer mode", "no restrictions" |

If `risk_score > 70` (configurable in `runtime-config.json`), the request is **blocked** before any model call.

### API Key Protection
Health and analysis responses are checked to ensure API keys (prefixes `tk_`, `AIzaSy`) never leak in responses.

---

## Guardian Route System

The Guardian Route compares the fastest route with a comfort-aware alternative:

- Adds buffer time for high-fatigue routes
- Considers energy preference (low energy = more buffer)
- Reports: fastest route minutes, guardian route minutes, tradeoff minutes, and reasoning signals
- Uses proxy signals (not real-time traffic data)

---

## Database & Persistence

SQLite database (`travy.db`) stores:

| Table | Purpose |
|---|---|
| `analyses` | Phase 1 analysis results (parsed constraints, security, intent, route decision) |
| `traces` | Step-by-step execution traces (task, route, status, cost, reason) |
| `results` | Generated itinerary results with validation reports and API evidence |
| `api_calls` | External API call logs (latency, status, provider) |

All persistence is managed through `persistence_service.py` with class methods:
- `init_db()` — Creates tables on startup
- `save_analysis()` / `get_analysis()`
- `save_trace()` / `get_traces()`
- `save_result()` / `get_result()`
- `reset_db()` — Clears all data (used in tests)

---

## Testing

### Backend Tests (31 total)
Run with:
```powershell
cd backend
.\.venv\Scripts\pytest
```

| Test File | Count | Coverage |
|---|---|---|
| `test_health.py` | 2 | Health and readiness endpoints |
| `test_otari_client_mock.py` | 5 | Otari client mock behavior, error handling |
| `test_phase2.py` | 16 | Constraint parsing (city, group size, budget, moods, time, energy, vague prompts, injection, booking, budget modes) |
| `test_phase3_phase4.py` | 8 | End-to-end flow (analyze → generate), critical budget mode, invented place rejection, integration health, API key masking, demo scenarios |

Tests mock external APIs (Nominatim, Overpass) at the module level to run fully offline.

### Frontend Tests
```powershell
npx playwright test
```

---

## How to Run

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.12+ and **pip**

### 1. Clone and install frontend dependencies
```powershell
cd d:\travy
npm install
```

### 2. Set up the backend virtual environment
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Configure environment variables
```powershell
cd d:\travy
copy .env.example .env
# Edit .env with your OTARI_API_KEY
```

### 4. Start the backend (port 8080)
```powershell
cd backend
.\.venv\Scripts\uvicorn app.main:app --port 8080 --reload
```

### 5. Start the frontend (port 3000)
```powershell
cd d:\travy
npm run dev
```

### 6. Open in browser
Navigate to `http://localhost:3000/planner`

---

## Design Principles

1. **Accuracy > Realism > Explainability > Optimization > AI Usage** — Every recommendation must be backed by real data.
2. **Zero fabrication** — If real data cannot be found, fail gracefully with an explanation. Never invent locations, prices, or ratings.
3. **Config-driven** — Scoring weights, budget thresholds, security parameters, and model pricing are all in JSON config files, not hardcoded.
4. **Graceful degradation** — If the LLM is unavailable or budget is depleted, the system falls back to a deterministic local builder that still uses real place data.
5. **Explainable decisions** — Every stop includes `why_selected` reasons referencing actual fit scores, costs, and constraint matches.
6. **Cost transparency** — Every API call, model invocation, and routing decision is logged in the execution trace.

---

*Generated on 2026-06-27. This document reflects the current state of the Travy codebase.*
