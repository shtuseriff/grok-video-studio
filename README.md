# Grok Video Studio

A local-first web app for generating and chaining AI video clips using xAI's [Grok Imagine Video](https://docs.x.ai/developers/models) API. Upload an image, write a prompt, and iterate on the result — or chain clips together into multi-part sequences with automatic frame continuity.

## Why this exists

Iterating on AI video generation is expensive and tedious. You fire off a prompt, wait, get something back, tweak the prompt, wait again. Grok Video Studio adds a workflow layer that makes the loop cheaper and faster:

- **Preflight checks** — a 1-second 480p test render ($0.05) catches moderation rejections before you commit to the full generation
- **Frame extension** — extract the last frame of any clip and use it as the seed for the next, maintaining visual continuity across a sequence
- **Prompt refinement** — optionally run your prompt through Grok 4.1 with the input image to get a version tuned to the visual content
- **Cost tracking** — per-session cost breakdown with optional budget caps so you don't accidentally burn through credits

## Quick start

### Prerequisites

| Dependency | Version | Install |
|---|---|---|
| Python | 3.13+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 23+ | [nodejs.org](https://nodejs.org/) (or `nvm use` in `web/`) |
| ffmpeg | any recent | `brew install ffmpeg` / `apt install ffmpeg` / `scoop install ffmpeg` |
| xAI API key | — | [x.ai](https://x.ai) |

### Setup

```bash
git clone https://github.com/<your-org>/grokv.git
cd grokv

# Python backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# React frontend
cd web && npm install && cd ..
```

### Run

Start both servers (two terminals, or use `just dev`):

```bash
# Terminal 1 — API (port 8000)
source .venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend (port 5173)
cd web && npm run dev
```

Open **http://localhost:5173**.

### Using just (recommended)

If you have [just](https://github.com/casey/just) installed:

```bash
just setup     # Create venv, install Python + Node deps
just dev       # Start both servers in parallel
just api       # Start only the API server
just web       # Start only the frontend dev server
just check     # Verify all prerequisites are installed
```

## Usage

### 1. Get your API key

Sign up at [x.ai](https://x.ai) and create an API key with access to `grok-imagine-video` and `grok-4-1-fast-reasoning`. Paste it into the **API Key** field in the sidebar. The key is sent per-request and never stored on the server.

### 2. Generate a single clip

1. Upload an image (JPEG, PNG, GIF, or WebP)
2. Write a prompt describing the desired motion
3. Click **Generate**
4. Preflight runs first (1s @ 480p) — if it passes, the full video generates at your chosen duration and resolution
5. Review the result: **continue**, **regenerate**, or **stop**

### 3. Multi-part sequences

1. Enter your prompt and click **Generate** — the first clip generates from your uploaded image
2. After each clip, click **Extend** to continue the sequence
3. The app extracts the last frame automatically and uses it as the seed for the next prompt
4. Each clip goes through the same preflight/generate/review loop

### 4. Prompt refinement

Toggle **Refine with Grok** to send each prompt through Grok 4.1 along with the current input image. The model returns a refined version tuned to the visual content. You can approve or reject each refinement, or enable **Auto-accept** to skip the review step.

### 5. Image analysis (grounding text)

Click **Analyze Image** to generate a detailed description of the uploaded image using Grok 4.1. This description is prepended to every prompt as grounding context, helping maintain character and setting consistency across clips.

## Features

- **Single & multi-part generation** — one clip or a chained sequence from the same starting image
- **Extend from last frame** — continue a session by extracting the final frame of the last clip
- **Preflight checks** — cheap 1-second test render before the full generation
- **Prompt refinement** — optional Grok 4.1 pass to tune prompts against the input image
- **Image analysis** — auto-describe an image for grounding context
- **Interactive review loop** — approve, regenerate, or stop after each clip
- **Session management** — persistent sessions with JSON state, cost ledger, and generated assets
- **Cost tracking** — per-item breakdown with configurable pricing and budget caps
- **HLS playlists** — `.m3u8` playlists for completed sessions
- **Session archives** — download any session as a `.zip` with an auto-generated HTML storyboard
- **Fork from any clip** — branch a new session from any point in an existing sequence

## Architecture

```
grokv/
├── api/                  # Python backend (FastAPI)
│   ├── main.py           # HTTP endpoints & request routing
│   ├── core.py           # xAI SDK wrappers (generate, preflight, refine, analyze)
│   ├── session.py        # Session state machine & manager
│   ├── pricing.py        # Pricing configuration loader
│   └── storyboard.py     # HTML storyboard generator for archives
├── web/                  # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx       # Main application component
│   │   ├── styles.css    # Dark-mode styling
│   │   └── main.jsx      # Entry point
│   ├── index.html
│   └── vite.config.js
├── sessions/             # Generated session data (created at runtime)
├── pricing.json          # Per-second cost configuration
├── justfile              # Task runner commands
├── requirements.txt      # Python dependencies
└── README.md
```

The backend runs on **port 8000**, the frontend dev server on **port 5173**. The frontend communicates with the backend via REST at `http://127.0.0.1:8000/api/`.

## Pricing

Generation costs are defined in `pricing.json`:

```json
{
  "currency": "USD",
  "models": {
    "grok-imagine-video": {
      "per_second": {
        "480p": 0.05,
        "720p": 0.05
      }
    }
  },
  "violation_fee": 0.05
}
```

- Preflight checks cost 1 second at 480p ($0.05)
- Moderation violations incur the `violation_fee`
- Edit the file and click **Refresh Pricing** in the UI to update without restarting

## CLI tools

Standalone scripts for use outside the web UI:

```bash
# Generate a single video
XAI_API_KEY=xai-... python generate_video.py -i image.png -p "A slow zoom out"

# Generate a multi-part sequence from numbered prompt files (1.txt, 2.txt, ...)
XAI_API_KEY=xai-... python generate_multi_video.py -i image.png -n 5

# Extract the last frame of a video
python extract_final_frame.py -v clip.mp4

# Verify all sessions and download missing files
python verify_sessions.py
python verify_sessions.py --dry-run
```

## API reference

All endpoints are prefixed with `/api`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/sessions` | List all sessions (most recent first) |
| `GET` | `/api/sessions/{id}` | Get session state |
| `POST` | `/api/single` | Start a single-clip generation |
| `POST` | `/api/multi` | Start a multi-clip generation (or extend via `session_id`) |
| `POST` | `/api/sessions/{id}/action` | Submit an action (`continue`, `regenerate`, `stop`, `use_refined`, `use_original`) |
| `POST` | `/api/sessions/{id}/title` | Rename a session |
| `POST` | `/api/sessions/{id}/extend-frame` | Extract the last frame for extending |
| `POST` | `/api/sessions/{id}/fork` | Fork a new session from a specific clip |
| `DELETE` | `/api/sessions/{id}` | Delete a session and its files |
| `GET` | `/api/sessions/{id}/archive` | Download session as `.zip` |
| `GET` | `/api/sessions/{id}/files/{name}` | Serve a generated file |
| `POST` | `/api/analyze-image` | Analyze an image for grounding text |
| `GET` | `/api/pricing` | Get current pricing |
| `POST` | `/api/pricing/refresh` | Reload `pricing.json` from disk |

## Session lifecycle

```
created → running → waiting → running → ... → completed
                                            → stopped
                                            → failed
```

- **running** — actively generating or processing
- **waiting** — paused for user input (approve clip, review refined prompt)
- **completed** — all clips finished, playlists written
- **stopped** — user stopped early; partial playlists written
- **failed** — unrecoverable error

## Contributing

Contributions are welcome. Some areas that could use help:

- **Break up `App.jsx`** — it's ~1400 lines doing everything; component extraction would help maintainability
- **WebSocket support** — replace polling with real-time status updates
- **Async backend** — convert synchronous xAI SDK calls to async
- **Tests** — unit tests for session state, cost calculations, playlist generation
- **Input validation** — image size limits, prompt length checks

## License

MIT
