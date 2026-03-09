# Grok Video Studio — Claude Context

## What this project is
A local-first web UI for xAI's `grok-imagine-video` API. Users upload an image, write prompts, and generate/chain video clips with preflight checks, cost tracking, and frame continuity between clips.

## Stack
- **Backend**: Python 3.13 / FastAPI / uvicorn — `api/` directory, runs on port 8000
- **Frontend**: React (Vite, JSX, no TypeScript) — `web/` directory, runs on port 5173
- **xAI SDK**: `xai-sdk` Python package — gRPC-based, 4 MB message size limit
- **Image processing**: Pillow (PIL) — used to resize images before API calls

## Key files
- `api/core.py` — xAI SDK wrappers: `preflight_check`, `generate_video`, `refine_prompt`, `analyze_image`, `load_image_as_data_url`
- `api/session.py` — session state machine, `SessionManager`, `SingleRequest`, `MultiRequest`
- `api/main.py` — FastAPI routes
- `api/pricing.py` — pricing config loader
- `web/src/App.jsx` — entire frontend (~1400 lines, monolithic by design for now)
- `pricing.json` — per-second cost config, editable at runtime

## Running locally
```bash
# Backend (port 8000)
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m uvicorn api.main:app --reload --port 8000

# Frontend (port 5173)
cd web && npm run dev
```
Or: `just dev` (requires [just](https://github.com/casey/just))

## Known constraints / gotchas
- **gRPC 4 MB limit**: xAI's API rejects messages > 4 MB. `load_image_as_data_url` in `core.py` auto-resizes images > 3 MB using Pillow before encoding. This happens transparently.
- **Synchronous SDK**: `xai-sdk` calls are blocking; sessions run in background threads via FastAPI `BackgroundTasks`.
- **No TypeScript**: frontend is plain JSX — no type checking.
- **API key**: passed per-request from the frontend, never persisted server-side.
- **ffmpeg required**: for `extract_last_frame` and `probe_duration`.

## Session lifecycle
`created → running → waiting → running → ... → completed | stopped | failed`

## Pricing
Edit `pricing.json` and click "Refresh Pricing" in the UI (calls `POST /api/pricing/refresh`) — no restart needed.
