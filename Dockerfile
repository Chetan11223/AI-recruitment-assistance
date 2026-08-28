# =========================================================================
# Stage 1: Build Frontend (React + Vite + Tailwind)
# =========================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
COPY frontend/.npmrc ./
RUN npm install --legacy-peer-deps

COPY frontend/ ./
RUN npm run build

# =========================================================================
# Stage 2: Production Python Backend & Unified Static Serving
# =========================================================================
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies required for native PDF extraction & healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and use isolated virtual environment (best practice, eliminates root pip warnings)
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python backend dependencies in virtual environment
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy application source code
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV LLM_PROVIDER=mock

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start FastAPI application
CMD ["sh", "-c", "python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
