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

### Running

```bash
uvicorn backend.app:app --reload
```

API runs at `http://127.0.0.1:8000`.
Interactive docs at `http://127.0.0.1:8000/docs`.

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
| `text` | string | Yes | — | Text to summarize (min 50 chars) |
| `min_length` | integer | No | 30 | Minimum summary length in tokens (10–100) |
| `max_length` | integer | No | 130 | Maximum summary length in tokens (50–300) |

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
