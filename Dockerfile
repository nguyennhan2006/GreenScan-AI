# --- web UI: built once, served by the API on the same port -------------------
FROM node:22-slim AS ui
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- API + UI ----------------------------------------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QUANTUM_PROFILE=offline \
    QUANTUM_UI_DIR=/app/frontend/dist

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-eng tesseract-ocr-vie \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
RUN pip install --no-cache-dir .
COPY data ./data
COPY --from=ui /ui/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "quantum_gw.api:app", "--host", "0.0.0.0", "--port", "8000"]
