import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from needle_api.engine import ExtractorEngine
from needle_api.models import (
    ErrorResponse,
    ExtractRequest,
    ExtractionResult,
    HealthResponse,
)

logger = logging.getLogger("needle_api")

engine = ExtractorEngine()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    info = engine.start()
    logger.info("Engine started: %s", info)
    yield
    engine.close()
    logger.info("Engine closed")


app = FastAPI(
    title="Needle Extraction API",
    version="0.1.0",
    description="JSON extraction from unstructured text using needl (Cactus Compute)",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status=engine.info.get("status", "unknown"),
        weights=engine.info.get("weights", "unknown"),
        generation=engine.info.get("generation", 3),
        loaded=engine.info.get("loaded", False),
    )


@app.post(
    "/extract",
    response_model=ExtractionResult,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal error"},
    },
)
async def extract(req: ExtractRequest) -> ExtractionResult:
    """Extract structured data from unstructured text.

    Provide a JSON Schema describing the fields you want, and unstructured text
    containing the data. The model returns typed field values with a confidence
    score.
    """
    # Validate schema shape
    schema = req.schema_
    if not isinstance(schema.get("parameters"), dict):
        raise HTTPException(
            status_code=422,
            detail="schema must have a 'parameters' object with 'properties'",
        )

    logger.info(
        "Extract request: %d chars, schema=%s, strict=%s",
        len(req.text),
        schema.get("name", "unnamed"),
        req.strict,
    )

    try:
        result = engine.extract(
            req.text,
            schema,
            strict=req.strict,
            max_new_tokens=req.max_new_tokens,
        )
    except ValueError as exc:
        logger.warning("Extraction validation error: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=str(exc))

    return ExtractionResult(**result)


def run_app(host: str = "0.0.0.0", port: int = 8765) -> None:
    """Run the API server with uvicorn."""
    import uvicorn

    uvicorn.run(
        "needle_api.app:app",
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    run_app()
