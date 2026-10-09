from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline


# ── Model loading ──────────────────────────────────────────────────────────────

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once at startup and release on shutdown."""
    print("Loading summarization model...")
    ml_models["summarizer"] = pipeline(
        "summarization", model="sshleifer/distilbart-cnn-12-6"
    )
    print("Model ready.")
    yield
    ml_models.clear()


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Text Summarizer API",
    description="Summarize text using sshleifer/distilbart-cnn-12-6.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Schemas ────────────────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=50, description="Text to summarize (min 50 chars)")
    min_length: int = Field(30, ge=10, le=100, description="Minimum summary length in tokens")
    max_length: int = Field(130, ge=50, le=300, description="Maximum summary length in tokens")


class SummarizeResponse(BaseModel):
    summary: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
def health():
    """Check that the API and model are running."""
    return {"status": "ok", "model": "sshleifer/distilbart-cnn-12-6"}


@app.post("/summarize", response_model=SummarizeResponse, tags=["Summarization"])
def summarize(request: SummarizeRequest):
    """
    Summarize the provided text.

    - **text**: the content to summarize (at least 50 characters)
    - **min_length**: minimum token length of the summary (default 30)
    - **max_length**: maximum token length of the summary (default 130)
    """
    if request.min_length >= request.max_length:
        raise HTTPException(
            status_code=422, detail="min_length must be less than max_length"
        )

    result = ml_models["summarizer"](
        request.text,
        min_length=request.min_length,
        max_length=request.max_length,
        do_sample=False,
    )
    return SummarizeResponse(summary=result[0]["summary_text"])
