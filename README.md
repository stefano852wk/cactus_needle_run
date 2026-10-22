# Needle Extraction API

A lightweight JSON extraction API powered by [Needle](https://github.com/cactus-compute/needle) — a tiny on-device model designed for structured data extraction.

## Prerequisites

- **Python 3.12+** with [uv](https://docs.astral.sh/uv/) installed
- **Needle 3 model weights** — download with:
  ```sh
  needle download needle3
  ```
  This produces `needle3.cact` (~35 MB) which is required to run the API.

## Quickstart

```sh
# Install dependencies
uv sync

# Start the API server (requires needle3.cact in the project root)
uv run python main.py
```

The server listens on `http://0.0.0.0:8765`.

## API

### `POST /extract`

Extract structured fields from unstructured text.

```json
{
  "text": "Invoice INV-2024-0423 from Acme Corp dated 2024-03-15 for $1,234.56",
  "schema": {
    "name": "invoice",
    "description": "Extract invoice details",
    "parameters": {
      "type": "object",
      "properties": {
        "invoice_number": {"type": "string", "description": "Invoice ID"},
        "vendor":        {"type": "string", "description": "Company name"},
        "date":          {"type": "string", "format": "date", "description": "Invoice date"},
        "total":         {"type": "number", "description": "Total amount"}
      },
      "required": ["invoice_number", "vendor", "total"]
    }
  }
}
```

Response:

```json
{
  "status": "ok",
  "extracted": { "invoice_number": "INV-2024-0423", ... },
  "confidence": 0.43,
  "reasoning": "invoice_number 'INV-2024-0423' from query; ...",
  "timing": { "prefill_tps": 41, "decode_tps": 36, "peak_ram_mb": 105 }
}
```

### `GET /health`

Returns model status and loaded flag.

## Language support

- **English** — reliable extraction with meaningful confidence scores (~0.3–0.5).
- **CJK (Chinese, Japanese, Korean)** — not supported. The model can't segment Asian text semantically. Numbers and ASCII codes within CJK text may still extract correctly.

## Docker

A prebuilt image is available at `docker.io/stefano852wk/needle-api:0.1.0`.

To run it:

```sh
docker pull docker.io/stefano852wk/needle-api:0.1.0
docker run -d -p 8765:8765 docker.io/stefano852wk/needle-api:0.1.0
```

The image includes `needle3.cact` and the pre-downloaded engine so no additional setup is needed.

## Project structure

```
needle_use/
├── needle3.cact          # Model weights (not in git — download separately)
├── pyproject.toml        # Dependencies: cactus-needle, fastapi, uvicorn, pydantic
├── main.py               # Entry point
├── needle_api/           # API package
│   ├── app.py            # FastAPI app (GET /health, POST /extract)
│   ├── engine.py         # Needle wrapper
│   └── models.py         # Request/response schemas
├── Dockerfile            # Container image
└── download_engine.py    # Build-time script to cache the Needle engine
```
