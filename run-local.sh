#!/bin/bash
# run-local.sh — Run the Live AI Tutor locally (backend + frontend)
# Usage: ./run-local.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Track child PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Shutting down..."
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && echo "Stopped frontend (PID $FRONTEND_PID)"
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null && echo "Stopped backend (PID $BACKEND_PID)"
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── Pre-flight checks ──────────────────────────────────────────────

echo "=== Live AI Tutor — Local Dev ==="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
    echo "Error: node is not installed."
    exit 1
fi

# Check backend .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "Error: backend/.env not found."
    echo "Copy backend/.env.example to backend/.env and fill in your API keys."
    exit 1
fi

# ── Backend setup ───────────────────────────────────────────────────

echo "[backend] Setting up Python environment..."

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "[backend] Creating virtual environment..."
    python3 -m venv "$BACKEND_DIR/venv"
fi

source "$BACKEND_DIR/venv/bin/activate"

echo "[backend] Installing dependencies..."
pip install -q -r "$BACKEND_DIR/requirements.txt"

# ── Frontend setup ──────────────────────────────────────────────────

echo "[frontend] Installing dependencies..."
(cd "$FRONTEND_DIR" && npm install --silent)

# ── Start services ──────────────────────────────────────────────────

echo ""
echo "[backend] Starting FastAPI on http://localhost:$BACKEND_PORT ..."
(cd "$BACKEND_DIR" && uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload) &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

echo "[frontend] Starting Vite dev server on http://localhost:$FRONTEND_PORT ..."
(cd "$FRONTEND_DIR" && VITE_BACKEND_URL="http://localhost:$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT") &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  API docs: http://localhost:$BACKEND_PORT/docs"
echo "============================================"
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait for either process to exit
wait
