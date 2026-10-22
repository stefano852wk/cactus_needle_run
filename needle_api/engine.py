import json
import logging
import os
from typing import Any

import needle

logger = logging.getLogger("needle_api.engine")

_EXTRACTOR_WEIGHTS = os.environ.get(
    "NEEDLE_WEIGHTS",
    "needle3.cact",
)


class ExtractorEngine:
    """Manages extraction using Needle.

    Each request gets a fresh Needle instance because the schema changes
    per request. The model weights are loaded once from disk cache.
    """

    def __init__(self, weights: str | None = None, generation: int = 3):
        self._weights = weights or _EXTRACTOR_WEIGHTS
        self._generation = generation
        self._info: dict[str, Any] = {}

    def start(self) -> dict[str, Any]:
        """Verify the model loads and is usable."""
        logger.info("Verifying needle weights at %s", self._weights)
        dummy = {
            "name": "ping",
            "description": "Health check",
            "parameters": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                },
            },
        }
        agent = needle.Needle(tools=[dummy], weights=self._weights)
        agent.complete("say ok")
        agent.close()
        logger.info("Needle engine ready")
        self._info = {
            "status": "ready",
            "weights": os.path.basename(self._weights),
            "generation": self._generation,
        }
        return self._info

    def extract(
        self,
        text: str,
        schema: dict,
        *,
        strict: bool = True,
        max_new_tokens: int = 1024,
    ) -> dict[str, Any]:
        """Run extraction with a fresh Needle instance."""
        agent = needle.Needle(
            tools=[schema],
            weights=self._weights,
        )
        try:
            response = agent.complete(text, max_new_tokens=max_new_tokens)
        finally:
            agent.close()

        calls = response.get("function_calls") or []
        suppressed = response.get("suppressed_calls") or []

        extracted = calls[0]["arguments"] if calls else None

        if extracted is None and suppressed:
            extracted = suppressed[0].get("arguments")

        return {
            "extracted": extracted,
            "confidence": response.get("confidence"),
            "reasoning": response.get("reasoning"),
            "validation": response.get("validation"),
            "suppressed": bool(not calls and suppressed),
            "timing": {
                "prefill_tps": response.get("prefill_tps"),
                "decode_tps": response.get("decode_tps"),
                "peak_ram_mb": response.get("peak_ram_mb"),
            },
        }

    def close(self) -> None:
        logger.info("Engine closed (no persistent agent to clean up)")

    @property
    def info(self) -> dict[str, Any]:
        return {**self._info, "loaded": True}
