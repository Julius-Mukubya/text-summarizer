import gradio as gr
from transformers import pipeline

# Load the summarization pipeline once at startup
print("Loading model... this may take a moment on first run.")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
print("Model loaded successfully!")


def summarize_text(text: str, min_length: int, max_length: int) -> str:
    """
    Summarize the input text using distilbart-cnn-12-6.

    Args:
        text: The text to summarize.
        min_length: Minimum number of tokens in the summary.
        max_length: Maximum number of tokens in the summary.

    Returns:
        The generated summary string.
    """
    if not text or not text.strip():
        return "Please enter some text to summarize."

    if min_length >= max_length:
        return "Min length must be less than max length."

    # The model handles truncation internally; do_sample=False for deterministic output
    result = summarizer(
        text,
        min_length=min_length,
        max_length=max_length,
        do_sample=False,
    )
    return result[0]["summary_text"]


# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="Text Summarizer", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # Text Summarizer
        Powered by **sshleifer/distilbart-cnn-12-6** - Paste any article or passage and get a concise summary.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            input_text = gr.Textbox(
                label="Input Text",
                placeholder="Paste your text here...",
                lines=12,
            )
        with gr.Column(scale=2):
            output_text = gr.Textbox(
                label="Summary",
                lines=12,
                interactive=False,
            )

    with gr.Row():
        min_len = gr.Slider(
            minimum=10,
            maximum=100,
            value=30,
            step=5,
            label="Min Summary Length (tokens)",
        )
        max_len = gr.Slider(
            minimum=50,
            maximum=300,
            value=130,
            step=10,
            label="Max Summary Length (tokens)",
        )

    with gr.Row():
        clear_btn = gr.ClearButton(components=[input_text, output_text], value="Clear")
        submit_btn = gr.Button("Summarize", variant="primary")

    submit_btn.click(
        fn=summarize_text,
        inputs=[input_text, min_len, max_len],
        outputs=output_text,
    )

    gr.Examples(
        examples=[
            [
                (
                    "The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, "
                    "and the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. "
                    "During its construction, the Eiffel Tower surpassed the Washington Monument to become the tallest "
                    "man-made structure in the world, a title it held for 41 years until the Chrysler Building in New York "
                    "City was finished in 1930. It was the first structure to reach a height of 300 metres. Due to the "
                    "addition of a broadcasting aerial at the top of the tower in 1957, it is now taller than the "
                    "Chrysler Building by 5.2 metres (17 ft). Excluding transmitters, the Eiffel Tower is the second "
                    "tallest free-standing structure in France after the Millau Viaduct."
                ),
                30,
                130,
            ]
        ],
        inputs=[input_text, min_len, max_len],
        label="Try an example",
    )

if __name__ == "__main__":
    demo.launch()
