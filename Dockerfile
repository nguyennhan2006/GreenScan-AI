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
# Seeded demo runs + the documents they cite (tools/build_demo_seed.py) and the
# start script that copies them into the store on first start (2026-11-09).
COPY deploy ./deploy

# Run as an unprivileged user with a writable store: Hugging Face Spaces runs
# containers as uid 1000, and nothing here needs root at run time.
# tr strips Windows line endings from the start script if it was edited on Windows.
RUN useradd -m -u 1000 greenscan \
    && mkdir -p /app/.quantum \
    && tr -d '\015' < /app/deploy/entrypoint.sh > /tmp/entrypoint.sh \
    && mv /tmp/entrypoint.sh /app/deploy/entrypoint.sh \
    && chmod +x /app/deploy/entrypoint.sh \
    && chown -R greenscan:greenscan /app
USER greenscan
ENV QUANTUM_HOME=/app/.quantum \
    QUANTUM_SEED_DIR=/app/deploy/seed \
    PORT=8000

EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT','8000'), timeout=8)"
CMD ["/app/deploy/entrypoint.sh"]
