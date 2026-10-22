# syntax=docker/dockerfile:1
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY needle3.cact /app/needle3.cact

COPY pyproject.toml uv.lock /app/

RUN pip install uv && \
    uv sync --no-dev

COPY needle3.cact /app/needle3.cact

# Pre-download the Needle engine so the container doesn't need Hugging Face at runtime
COPY download_engine.py /app/download_engine.py
RUN uv run python /app/download_engine.py && rm /app/download_engine.py

COPY needle_api/ /app/needle_api/
COPY main.py /app/

ENV NEEDLE_WEIGHTS=/app/needle3.cact
ENV NEEDLE_HOME=/root/.cache/needle

EXPOSE 8765

CMD ["uv", "run", "python", "main.py"]
