# Stage 1: Build the React frontend
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_GEMINI_API_KEY
ENV VITE_GEMINI_API_KEY=$VITE_GEMINI_API_KEY
# In production the frontend is served from the same origin as the backend,
# so VITE_BACKEND_URL is left empty (relative URLs).
ENV VITE_BACKEND_URL=""
RUN npm run build

# Stage 2: Python backend + built frontend
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=True
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist ./static

# Cloud Run sets $PORT (default 8080)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
