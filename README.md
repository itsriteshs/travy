# Travy - Mozilla.ai Cost-Aware AI Travel Assistant

Fresh MVP implementation from scratch in this repository.

## Stack

- Backend: FastAPI
- Frontend: React + Tailwind + shadcn/ui-style components
- Decisioning: Local Encoderfile-style + Llamafile-style analyzers + Any-Agent inspired agents
- Generation: Otari client stub

## Mandatory Flow Implemented

User Prompt
-> Encoderfile Embedding Generation
-> Encoderfile Intent Classification
-> Llamafile Security Analysis
-> Llamafile Complexity Analysis
-> Llamafile Cost Estimation
-> Budget Validation
-> Dynamic Model Selection
-> Otari Request
-> Travel Itinerary Response

Otari is called only after local analysis and budget/security checks.

## Project Structure

backend/
- agents/
- router/
- security/
- budget/
- tools/
- otari/
- api/

frontend/
- React app with chat box, itinerary card, transparency panel, and budget bar

## Installed Dependencies (local to this project)

- Backend venv at backend/.venv (Python 3.12)
- Backend packages from backend/requirements.txt
- Frontend npm packages in frontend/node_modules

## Run

Backend:

1. cd backend
2. .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

Frontend:

1. cd frontend
2. npm run dev

Open http://localhost:5173

## Run Otari (local gateway)

Otari repo has been checked out at `otari/`.

1. Start Docker Desktop and wait until Docker engine is running.
2. From project root: `./run-otari.ps1`
3. Health check: `http://127.0.0.1:8010/health`

Notes:

- Otari host port is mapped to `8010` to avoid conflict with Travy backend on `8000`.
- Otari Postgres host port is mapped to `5434`.

### One-command setup and run (Windows PowerShell)

From the project root:

1. .\install-all.ps1
2. In terminal 1: .\run-backend.ps1
3. In terminal 2: .\run-frontend.ps1

## Notes

- Global budget starts at $2 and is enforced before generation.
- BLOCKED security requests never reach Otari.
- Transparency fields are returned for every request.
- Travison image-to-trip flow requires GEMINI_API_KEY in backend/.env.
- Travison endpoint: POST /travison (image upload -> Gemini vision analysis -> Otari similar-place itinerary).
- Local routing aliases map to provider models via environment variables:
	- otari-small -> OTARI_SMALL_MODEL
	- otari-medium -> OTARI_MEDIUM_MODEL
	- otari-large -> OTARI_LARGE_MODEL
	- otari-vision -> OTARI_VISION_MODEL
- City-aware itinerary prompts are optimized for New Delhi, Coimbatore, and New York City.

## Provider setup check

After backend starts:

- GET http://127.0.0.1:8000/provider-check

If chat returns an Otari network error, verify OTARI_BASE_URL in backend/.env.
The URL must point to a reachable OpenAI-compatible endpoint that supports /v1/chat/completions.
