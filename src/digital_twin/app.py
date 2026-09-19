import asyncio
from agents import Agent, Runner, trace, function_tool, SQLiteSession
from dotenv import load_dotenv
import gradio as gr
from digital_twin.context import TWIN_SYSTEM_PROMPT, CAREER_VALIDATOR_PROMPT
from tools.notification_tool import record_user_details, record_unknown_question
import json
import base64

load_dotenv(override=True)
MODEL = "gpt-5.5"

async def validate_response(response_text, historyMessage):
    messages = list(historyMessage)
    message = f"Validate this response:\n\n{response_text}"
    messages.append({"role": "user", "content": message})
    
    validator = Agent(
        name="Career Validator",
        instructions=CAREER_VALIDATOR_PROMPT,
        model=MODEL
    )

    result = await Runner.run(validator, messages)
    return json.loads(result.final_output)

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


LOADING_MESSAGE = "Thinking..."


async def respond(message, history):
    history = list(history or [])
    if not str(message or "").strip():
        yield gr.update(), history, gr.update(), gr.update()
        return

    history.append({"role": "user", "content": message})
    loading_history = history + [{"role": "assistant", "content": LOADING_MESSAGE}]
    yield (
        gr.update(value="", interactive=False),
        loading_history,
        gr.update(visible=False),
        gr.update(visible=True),
    )

    try:
        historyMessage = cleanHistoryMessage(history)

        agent = Agent(
            name="Arianne's Digital Twin",
            instructions=TWIN_SYSTEM_PROMPT,
            model=MODEL
        )
        result = await Runner.run(agent, historyMessage)
        twin_response = result.final_output

        validation = await validate_response(twin_response, historyMessage)

        if not validation["approved"]:
            assistant_content = validation["revision"]
        else:
            assistant_content = twin_response
    except Exception:
        assistant_content = "Sorry, something went wrong. Please try again."

    completed_history = history + [{"role": "assistant", "content": assistant_content}]
    yield (
        gr.update(value="", interactive=True),
        completed_history,
        gr.update(visible=False),
        gr.update(visible=True),
    )


with gr.Blocks(fill_width=True) as demo:
    image_path = "src/digital_twin/digital_twin_avatar.png"
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
            btn1 = gr.Button(
                "What is your current role and what are your working on right now?",
                elem_classes="pill-button",
            )
            btn2 = gr.Button(
                "What is your primary programming language?",
                elem_classes="pill-button",
            )
            btn3 = gr.Button("I'd like to get in touch", elem_classes="pill-button")

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
        )

    # Triggers the transition: hides welcome_screen text/pills, reveals chatbot
    user_input.submit(
        respond,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot, welcome_screen, chatbot],
        show_progress="hidden",
    )

    btn1.click(lambda: ("What is your current role and what are your working on right now?"), None, user_input,)
    btn2.click(lambda: "What is your primary programming language?", None, user_input)
    btn3.click(lambda: "I'd like to get in touch", None, user_input)

if __name__ == "__main__":
    demo.launch(css_paths=["src/digital_twin/styles.css"], footer_links=["gradio", "settings"])
