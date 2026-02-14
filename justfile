# Grok Video Studio

set dotenv-load

venv := ".venv"
python := venv / "bin/python"
pip := venv / "bin/pip"
uvicorn := venv / "bin/uvicorn"

# List available commands
default:
    @just --list

# Verify all prerequisites are installed
check:
    #!/usr/bin/env bash
    set -euo pipefail
    ok=true

    check() {
        if command -v "$1" &>/dev/null; then
            printf "  %-12s %s\n" "$1" "$(eval "$2" 2>&1 | head -1)"
        else
            printf "  %-12s MISSING\n" "$1"
            ok=false
        fi
    }

    echo "Prerequisites:"
    check python3   "python3 --version"
    check node      "node --version"
    check npm       "npm --version"
    check ffmpeg    "ffmpeg -version"
    check ffprobe   "ffprobe -version"

    if [ -f "{{ venv }}/bin/python" ]; then
        printf "  %-12s %s\n" "venv" "ok ({{ venv }})"
    else
        printf "  %-12s MISSING — run 'just setup'\n" "venv"
        ok=false
    fi

    if [ -d "web/node_modules" ]; then
        printf "  %-12s %s\n" "node_modules" "ok"
    else
        printf "  %-12s MISSING — run 'just setup'\n" "node_modules"
        ok=false
    fi

    echo ""
    if $ok; then
        echo "All good."
    else
        echo "Some prerequisites are missing. Install them and run 'just setup'."
        exit 1
    fi

# Create venv and install all dependencies
setup:
    python3 -m venv {{ venv }}
    {{ pip }} install -r requirements.txt
    cd web && npm install

# Install Python dependencies only
setup-api:
    python3 -m venv {{ venv }}
    {{ pip }} install -r requirements.txt

# Install Node dependencies only
setup-web:
    cd web && npm install

# Start the API server (port 8000)
api:
    {{ uvicorn }} api.main:app --reload --port 8000

# Start the frontend dev server (port 5173)
web:
    cd web && npm run dev

# Start both servers in parallel
dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    {{ uvicorn }} api.main:app --reload --port 8000 &
    cd web && npm run dev &
    wait

# Build the frontend for production
build:
    cd web && npm run build

# Clean generated sessions, logs, and build artifacts
clean:
    rm -rf sessions/
    rm -f generate_video.log generate_multi_video.log
    cd web && rm -rf dist

# Clean everything including venv and node_modules
clean-all: clean
    rm -rf {{ venv }}
    cd web && rm -rf node_modules

# Verify sessions and report missing files (dry run)
verify-sessions:
    {{ python }} verify_sessions.py --dry-run

# Verify sessions and download missing files
fix-sessions:
    {{ python }} verify_sessions.py
