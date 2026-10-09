# Text Summarizer API

A REST API for text summarization powered by [sshleifer/distilbart-cnn-12-6](https://huggingface.co/sshleifer/distilbart-cnn-12-6), built with FastAPI.

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Interactive docs are at `http://127.0.0.1:8000/docs`.

## Endpoints

### `GET /health`
Check that the API and model are running.

**Response**
```json
{ "status": "ok", "model": "sshleifer/distilbart-cnn-12-6" }
```

---

### `POST /summarize`
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

## Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [Transformers](https://huggingface.co/docs/transformers) (v4)
- [PyTorch](https://pytorch.org/) (CPU)
