from pathlib import Path
import asyncio
from agents import Agent, Runner, trace, function_tool, SQLiteSession
from dotenv import load_dotenv
import gradio as gr
from digital_twin.context import TWIN_SYSTEM_PROMPT, CAREER_VALIDATOR_PROMPT
from digital_twin.schemas import TwinReply, ValidationResult
from tools.notification_tool import record_user_details, record_unknown_question
import base64

load_dotenv(override=True)
MODEL = "gpt-5.5"
PACKAGE_DIR = Path(__file__).resolve().parent
APP_CSS = (PACKAGE_DIR / "styles.css").read_text(encoding="utf-8")
LOADING_MESSAGE = "Thinking..."
STOPPED_MESSAGE = "OK, I've stopped generating the response."
STREAM_CHUNK_CHARS = 28
STREAM_CHUNK_DELAY = 0.03
DEFAULT_SUGGESTIONS = [
    "What is your current role and what are you working on right now?",
    "What is your primary programming language?",
    "I'd like to get in touch",
]


async def validate_response(response_text, historyMessage):
    messages = list(historyMessage)
    message = f"Validate this response:\n\n{response_text}"
    messages.append({"role": "user", "content": message})
    
    validator = Agent(
        name="Career Validator",
        instructions=CAREER_VALIDATOR_PROMPT,
        model=MODEL,
        output_type=ValidationResult,
    )

    result = await Runner.run(validator, messages)
    return result.final_output

def cleanHistoryMessage(history):
    messages = []
    if not history:
        return messages

    for item in history:
        content = item.get("content", "")
        # Gradio 6 content structure safety check:
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and "text" in content[0]:
                content = content[0]["text"]
            else:
                content = str(content[0])
        elif isinstance(content, dict):
            content = content.get("text", str(content))
            
        messages.append({
            "role": item["role"],
            "content": str(content)
        })
    return messages


def pad_suggestions(suggestions):
    padded = [str(item).strip() for item in suggestions if str(item).strip()]
    padded.extend(DEFAULT_SUGGESTIONS)
    return padded[:3]


def suggestion_options(suggestions):
    return [{"label": text, "value": text} for text in pad_suggestions(suggestions)]


def iter_reply_prefixes(text):
    content = str(text or "")
    if not content:
        yield ""
        return

    index = 0
    length = len(content)
    while index < length:
        next_index = min(index + STREAM_CHUNK_CHARS, length)
        if next_index < length:
            space = content.find(" ", next_index - 1)
            newline = content.find("\n", next_index - 1)
            breaks = [value for value in (space, newline) if value >= next_index - 1]
            if breaks:
                next_index = min(breaks) + 1
        index = next_index
        yield content[:index]


async def respond(message, history):
    history = list(history or [])
    if not str(message or "").strip():
        yield gr.update(), history, gr.update(), gr.update()
        return

    history.append({"role": "user", "content": message})
    loading_history = history + [{"role": "assistant", "content": LOADING_MESSAGE}]
    yield (
        gr.update(value="", interactive=False, submit_btn=False, stop_btn=True),
        loading_history,
        gr.update(visible=False),
        gr.update(visible=True),
    )

    suggestions = list(DEFAULT_SUGGESTIONS)
    try:
        historyMessage = cleanHistoryMessage(history)

        agent = Agent(
            name="Arianne's Digital Twin",
            instructions=TWIN_SYSTEM_PROMPT,
            model=MODEL,
            output_type=TwinReply,
        )
        result = await Runner.run(agent, historyMessage)
        twin_output = result.final_output
        twin_response = twin_output.reply
        suggestions = pad_suggestions(twin_output.suggestions)

        validation = await validate_response(twin_response, historyMessage)

        if not validation.approved:
            assistant_content = validation.revision
        else:
            assistant_content = twin_response
    except Exception:
        assistant_content = "Sorry, something went wrong. Please try again."

    prefixes = list(iter_reply_prefixes(assistant_content))
    if not prefixes:
        prefixes = [assistant_content]

    for prefix in prefixes[:-1]:
        yield (
            gr.update(value="", interactive=False, submit_btn=False, stop_btn=True),
            history + [{"role": "assistant", "content": prefix}],
            gr.update(visible=False),
            gr.update(visible=True),
        )
        await asyncio.sleep(STREAM_CHUNK_DELAY)

    yield (
        gr.update(value="", interactive=True, submit_btn=True, stop_btn=False),
        history
        + [
            {
                "role": "assistant",
                "content": assistant_content,
                "options": suggestion_options(suggestions),
            }
        ],
        gr.update(visible=False),
        gr.update(visible=True),
    )


with gr.Blocks(fill_width=True) as demo:
    image_path = PACKAGE_DIR / "digital_twin_avatar.png"
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    # 1. The Avatar Image stays visible at the very top as a persistent header
    gr.HTML(
        f'<img src="data:image/png;base64,{encoded_string}" class="avatar-img" alt="Digital Twin Avatar">'
    )

    # 2. Original welcome container now holds only the text and buttons that hide
    with gr.Column(elem_classes="centered-container") as welcome_screen:
        gr.HTML(
            "<h1 class='main-title'>I'm Arianne's <em>digital twin.</em><br>I"
            " never sleep, so ask me anything.</h1>"
        )
        gr.HTML(
            "<p class='subtitle'>I know her career, background, skills and"
            " education. I can also connect you with her.</p>"
        )

        with gr.Row():
            btn1 = gr.Button(DEFAULT_SUGGESTIONS[0], elem_classes="pill-button")
            btn2 = gr.Button(DEFAULT_SUGGESTIONS[1], elem_classes="pill-button")
            btn3 = gr.Button(DEFAULT_SUGGESTIONS[2], elem_classes="pill-button")

    # 3. Chatbot display sits directly below the avatar header (Removed type="messages" for Gradio 6)
    chatbot = gr.Chatbot(
        elem_classes="chat-display",
        visible=False,
        height="70vh",
        show_label=False,
        buttons=[],
    )

    with gr.Row(elem_classes="input-wrapper"):
        user_input = gr.Textbox(
            show_label=False,
            placeholder="How can I help you today?",
            lines=1,
            max_lines=3,
            scale=4,
            submit_btn=True,
            stop_btn=False,
        )

    def restore_input():
        return gr.update(interactive=True, submit_btn=True, stop_btn=False)

    def stop_generation(history):
        history = list(history or [])
        stopped = {"role": "assistant", "content": STOPPED_MESSAGE}
        if history and history[-1].get("role") == "assistant":
            history[-1] = stopped
        else:
            history.append(stopped)
        return restore_input(), history

    # Triggers the transition: hides welcome_screen text/pills, reveals chatbot
    submit_event = user_input.submit(
        respond,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot, welcome_screen, chatbot],
        show_progress="hidden",
    )
    submit_event.then(
        restore_input,
        None,
        user_input,
        queue=False,
        show_progress="hidden",
    )

    PREFILL_DELAY = 0.28

    async def respond_from_prefill(message, history):
        text = str(message or "").strip()
        if not text:
            yield gr.update(), history, gr.update(), gr.update()
            return
        yield (
            gr.update(value=text, interactive=True, submit_btn=True, stop_btn=False),
            history,
            gr.update(),
            gr.update(),
        )
        await asyncio.sleep(PREFILL_DELAY)
        async for update in respond(text, history):
            yield update

    async def respond_from_option(evt: gr.SelectData, history):
        value = evt.value
        if isinstance(value, dict):
            value = value.get("value") or value.get("label") or ""
        async for update in respond_from_prefill(value, history):
            yield update

    def bind_suggestion_click(button, suggestion):
        async def respond_from_pill(history):
            async for update in respond_from_prefill(suggestion, history):
                yield update

        event = button.click(
            respond_from_pill,
            chatbot,
            [user_input, chatbot, welcome_screen, chatbot],
            show_progress="hidden",
        )
        event.then(
            restore_input,
            None,
            user_input,
            queue=False,
            show_progress="hidden",
        )
        return event

    pill_events = [
        bind_suggestion_click(btn1, DEFAULT_SUGGESTIONS[0]),
        bind_suggestion_click(btn2, DEFAULT_SUGGESTIONS[1]),
        bind_suggestion_click(btn3, DEFAULT_SUGGESTIONS[2]),
    ]
    option_event = chatbot.option_select(
        respond_from_option,
        chatbot,
        [user_input, chatbot, welcome_screen, chatbot],
        show_progress="hidden",
    )
    option_event.then(
        restore_input,
        None,
        user_input,
        queue=False,
        show_progress="hidden",
    )
    user_input.stop(
        stop_generation,
        chatbot,
        [user_input, chatbot],
        cancels=[submit_event, option_event, *pill_events],
        queue=False,
        show_progress="hidden",
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(css=APP_CSS, footer_links=[])
