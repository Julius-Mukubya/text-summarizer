# Text Summarizer

A text summarization project powered by [sshleifer/distilbart-cnn-12-6](https://huggingface.co/sshleifer/distilbart-cnn-12-6).

The project is split into two parts:
- **Backend** — a FastAPI REST API that runs the model
- **Frontend** — a Streamlit web interface that talks to the API

```
text-summarizer/
├── backend/
│   ├── app.py                  # FastAPI backend
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── streamlit_app.py        # Streamlit frontend
│   └── requirements.txt        # Frontend dependencies
├── .gitignore
└── README.md
```

---

## Backend (FastAPI)

### Setup

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
source venv/bin/activate         # Mac/Linux

pip install -r backend/requirements.txt
```

> **PyTorch install note** — `backend/requirements.txt` includes
> `--index-url https://download.pytorch.org/whl/cpu` so pip downloads the
> CPU-only PyTorch wheel (~250 MB) instead of the full CUDA build (~2 GB).
> If you need GPU support, remove that line and adjust the version specifier
> to match your CUDA version.

> **First-run download** — On the first startup the Hugging Face `transformers`
> library will download the model weights (~1.2 GB) to
> `~/.cache/huggingface/hub/`. Subsequent startups load from the local cache
> and are much faster. Make sure you have enough disk space and a stable
> internet connection for the first run.

### Running

```bash
uvicorn backend.app:app --reload
```

API runs at `http://127.0.0.1:8000`.
Interactive docs at `http://127.0.0.1:8000/docs`.

### Configuration

Copy the example env file and edit as needed:

```bash
cp backend/.env.example backend/.env
```

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:8501` | Comma-separated list of origins allowed to call the API |

`backend/.env` is loaded automatically on startup via `python-dotenv`. Any variable already set in the shell environment takes precedence over the file.

### Endpoints

#### `GET /health`
Check that the API and model are running.

```json
{ "status": "ok", "model": "sshleifer/distilbart-cnn-12-6" }
```

#### `POST /summarize`
Summarize a piece of text.

**Request body**
```json
{
  "text": "your long article or passage here...",
  "min_length": 30,
  "max_length": 130
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | Yes | — | Text to summarize (50–4 000 chars) |
| `min_length` | integer | No | 30 | Minimum summary length in tokens (10–100) |
| `max_length` | integer | No | 130 | Maximum summary length in tokens (50–300) |

> The 4 000-character cap on `text` maps to BART's ~1 024-token context window.
> Inputs beyond this limit would be silently truncated by the model, so the API
> rejects them with a 422 error instead.

**Response**
```json
{ "summary": "concise version of your text" }
```

**Example with curl**
```bash
curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "your long article text here...", "min_length": 30, "max_length": 130}'
```

---

## Frontend (Streamlit)

### Setup

```bash
pip install -r frontend/requirements.txt
```

### Running

Make sure the FastAPI backend is running first, then:

```bash
streamlit run frontend/streamlit_app.py
```

The interface opens automatically in your browser at `http://localhost:8501`.

### Configuration

Copy the example env file and edit as needed:

```bash
cp frontend/.env.example frontend/.env
```

| Variable | Default | Description |
|---|---|---|
| `API_URL` | `http://127.0.0.1:8000` | Base URL of the FastAPI backend |

`frontend/.env` is loaded automatically on startup via `python-dotenv`. Any variable already set in the shell environment takes precedence over the file.

### Features
- API health indicator — shows whether the backend is reachable
- Text input with min/max length sliders
- Word count comparison between original and summary
- Built-in example to test with

---

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) — REST API backend
- [Streamlit](https://streamlit.io/) — web frontend
- [Transformers](https://huggingface.co/docs/transformers) (v4) — summarization model
- [PyTorch](https://pytorch.org/) (CPU) — model inference
