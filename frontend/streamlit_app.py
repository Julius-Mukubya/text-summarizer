import os

from dotenv import load_dotenv
import requests
import streamlit as st

# Load variables from frontend/.env (if present) into os.environ.
# Values already set in the environment take precedence.
load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Text Summarizer",
    page_icon="📝",
    layout="centered",
)

# ── API config ─────────────────────────────────────────────────────────────────
# Override the default URL by setting the API_URL environment variable,
# e.g. export API_URL=http://myserver:8000 before running Streamlit.

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


def check_api_health() -> bool:
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def summarize(text: str, min_length: int, max_length: int) -> str:
    response = requests.post(
        f"{API_URL}/summarize",
        json={"text": text, "min_length": min_length, "max_length": max_length},
        timeout=120,
    )
    if response.status_code == 200:
        return response.json()["summary"]
    elif response.status_code == 422:
        detail = response.json().get("detail", "Invalid input.")
        raise ValueError(detail)
    else:
        raise RuntimeError(f"API error {response.status_code}: {response.text}")


# ── UI ─────────────────────────────────────────────────────────────────────────

st.title("Text Summarizer")
st.caption("Powered by sshleifer/distilbart-cnn-12-6 via FastAPI")

# API health indicator
if check_api_health():
    st.success("API is online", icon="✅")
else:
    st.error(
        f"Cannot reach the API at {API_URL}. "
        "Make sure the FastAPI server is running with `uvicorn app:app --reload`.",
        icon="🔴",
    )

st.divider()

# ── Example text ───────────────────────────────────────────────────────────────

EXAMPLE_TEXT = (
    "The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, "
    "and the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. "
    "During its construction, the Eiffel Tower surpassed the Washington Monument to become the tallest "
    "man-made structure in the world, a title it held for 41 years until the Chrysler Building in New York "
    "City was finished in 1930. It was the first structure to reach a height of 300 metres. Due to the "
    "addition of a broadcasting aerial at the top of the tower in 1957, it is now taller than the "
    "Chrysler Building by 5.2 metres (17 ft). Excluding transmitters, the Eiffel Tower is the second "
    "tallest free-standing structure in France after the Millau Viaduct."
)

# ── Input ──────────────────────────────────────────────────────────────────────
# Read any pre-loaded example from session state so the widget renders with it.
# Using pop() clears the flag in the same pass, avoiding a second rerun.

default_text = st.session_state.pop("example_loaded", "")

text_input = st.text_area(
    "Paste your text here",
    value=default_text,
    height=250,
    placeholder="Enter at least 50 characters...",
)

# Controls
col1, col2 = st.columns(2)
with col1:
    min_length = st.slider("Min summary length (tokens)", min_value=10, max_value=100, value=30, step=5)
with col2:
    max_length = st.slider("Max summary length (tokens)", min_value=50, max_value=300, value=130, step=10)

# Summarize button
if st.button("Summarize", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("Please enter some text first.")
    elif len(text_input.strip()) < 50:
        st.warning("Text must be at least 50 characters.")
    elif min_length >= max_length:
        st.warning("Min length must be less than max length.")
    else:
        with st.spinner("Summarizing..."):
            try:
                summary = summarize(text_input, min_length, max_length)
                st.subheader("Summary")
                st.write(summary)

                # Word count comparison
                original_words = len(text_input.split())
                summary_words = len(summary.split())
                reduction = round((1 - summary_words / original_words) * 100)
                st.caption(
                    f"Original: {original_words} words → Summary: {summary_words} words "
                    f"({reduction}% reduction)"
                )
            except ValueError as e:
                st.error(str(e))
            except RuntimeError as e:
                st.error(str(e))
            except requests.exceptions.Timeout:
                st.error("Request timed out. The model may still be loading — try again in a moment.")
            except requests.exceptions.ConnectionError:
                st.error("Lost connection to the API. Make sure the FastAPI server is still running.")

# Example
with st.expander("Try an example"):
    st.write(EXAMPLE_TEXT)
    if st.button("Load this example"):
        # Store the text so the text_area picks it up via value= on next render.
        st.session_state["example_loaded"] = EXAMPLE_TEXT
        st.rerun()
