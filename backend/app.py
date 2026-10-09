import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import pipeline

# Load variables from backend/.env (if present) into os.environ.
# Values already set in the environment take precedence.
load_dotenv()


# ── Model loading ──────────────────────────────────────────────────────────────

ml_models = {}

# BART's maximum context window is 1 024 tokens.  At ~4 chars/token that's
# roughly 4 000 characters, but to give headroom for tokenizer overhead we cap
# raw input at 4 000 characters.  Inputs beyond this would be silently truncated
# by the transformers pipeline, which can produce poor or misleading summaries.
MAX_TEXT_CHARS = 4_000


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

# ── CORS ───────────────────────────────────────────────────────────────────────
# Reads allowed origins from the CORS_ORIGINS environment variable as a
# comma-separated list, e.g.:
#   export CORS_ORIGINS=http://localhost:8501,https://myapp.example.com
# Defaults to the local Streamlit dev address when the variable is not set.

_raw_origins = os.environ.get("CORS_ORIGINS", "http://localhost:8501")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ── Schemas ────────────────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=50,
        max_length=MAX_TEXT_CHARS,
        description=(
            f"Text to summarize (min 50 chars, max {MAX_TEXT_CHARS} chars). "
            "BART's context window is ~1 024 tokens; longer inputs are capped here "
            "to prevent silent truncation."
        ),
    )
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

    - **text**: the content to summarize (50–4 000 characters)
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
