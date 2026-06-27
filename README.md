# Travy

Cost-aware social travel assistant for the Mozilla/Otari hack.

## Run Locally

Terminal 1, backend:

```bash
cd /Users/ritesh/travy
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8080 --reload
```

Terminal 2, frontend:

```bash
cd /Users/ritesh/travy
npm install
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8080 npm run dev
```

Open `http://localhost:3000`. If port `3000` is busy, Next will print the fallback URL.

## Demo Flow

1. Open `/planner`.
2. Analyze the default Delhi prompt.
3. Generate the plan and open `/results`.
4. Open `/ai-router` to show backend routing trace, budget, usage, and integration health.
5. Open `/security` to show backend prompt-injection scanning.
6. Open `/demo` to run backend scenarios:
   - valid Delhi plan
   - low budget
   - critical budget
   - prompt injection
   - vague prompt
   - booking out of scope
   - unsupported live crime data fallback

## Checks

Backend:

```bash
source .venv/bin/activate
PYTHONPATH=backend pytest -q backend/app/tests
```

Frontend:

```bash
npm run lint
npm run typecheck
npm run build
```
