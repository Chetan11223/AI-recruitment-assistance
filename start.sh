#!/usr/bin/env bash
set -e

echo "========================================================="
echo " Starting Resume Intelligence System (PageIndex + Agentic RAG)"
echo "========================================================="

# 1. Start Backend FastAPI
echo "Starting Backend FastAPI on http://localhost:8000..."
./venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Frontend Vite
echo "Starting Frontend on http://localhost:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGINT SIGTERM EXIT

wait
