from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    """Request body for the /extract endpoint."""

    text: str = Field(
        ...,  # required
        min_length=1,
        description="The unstructured text to extract data from",
    )
    schema_: dict = Field(
        ...,
        alias="schema",
        description="JSON Schema describing the fields to extract. "
        "Must have 'name', 'description', and 'parameters' with 'properties'.",
    )
    strict: bool = Field(
        default=True,
        description="When True, raises ExtractionValidationError for ungrounded "
        "dates/numbers not present in the input. Set False to get best-effort extraction.",
    )
    max_new_tokens: int = Field(
        default=1024,
        ge=64,
        le=16384,
        description="Maximum tokens to generate for the extraction response.",
    )


class ExtractionResult(BaseModel):
    """Successful extraction response."""

    status: str = "ok"
    extracted: dict | None = Field(
        description="The extracted fields as a flat JSON object, or null if "
        "the model could not match the input to the schema.",
    )
    confidence: float | None = Field(
        description="Calibrated confidence score [0, 1]. Values above ~0.5 "
        "indicate reliable extraction. Low values typically mean the input "
        "language or structure isn't well handled by the model.",
    )
    reasoning: str | None = Field(
        description="The model's step-by-step reasoning about what it extracted and why.",
    )
    validation: dict | None = Field(
        description="Validation metadata. `ungrounded` lists fields that were "
        "fabricated (not present in input); `negation` indicates the input "
        "was a negative/conditional request.",
    )
    suppressed: bool = Field(
        description="If True, the extraction was low-confidence and the result "
        "was placed in suppressed_calls rather than function_calls. The extracted "
        "data is still returned, but should be treated with extra caution.",
    )
    timing: dict | None = Field(
        description="Performance metrics: prefill_tps, decode_tps, peak_ram_mb.",
    )


class ErrorResponse(BaseModel):
    """Error response."""

    status: str = "error"
    detail: str
    code: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    weights: str
    generation: int
    loaded: bool
