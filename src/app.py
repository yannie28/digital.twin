import sys
from pathlib import Path

from fastapi import FastAPI
import gradio as gr

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from digital_twin.app import APP_CSS, demo  # noqa: E402

app = gr.mount_gradio_app(
    FastAPI(),
    demo,
    path="/",
    css=APP_CSS,
    footer_links=["gradio", "settings"],
)
