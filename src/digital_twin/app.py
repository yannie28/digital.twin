import asyncio
from agents import Agent, Runner, trace, function_tool, SQLiteSession
from dotenv import load_dotenv
import gradio as gr
from digital_twin.context import TWIN_SYSTEM_PROMPT, CAREER_VALIDATOR_PROMPT
from tools.notification_tool import record_user_details, record_unknown_question
import json

load_dotenv(override=True)
MODEL = "gpt-5.5"

async def chat(message, history):
    messages = retrieveMessage(message, history)  
    agent = Agent(
        name="Arianne's Digital Twin",
        instructions=TWIN_SYSTEM_PROMPT,
        model=MODEL
    )
    result = await Runner.run(agent, messages)
    twin_response = result.final_output

    validation = await validate_response(twin_response, history)

    if not validation["approved"]:
        return validation["revision"]

    return twin_response

async def validate_response(response_text, history):
    message = f"Validate this response:\n\n{response_text}"
    messages = retrieveMessage(message, history)  
    validator = Agent(
        name="Career Validator",
        instructions=CAREER_VALIDATOR_PROMPT,
        model=MODEL
    )

    result = await Runner.run(validator, messages)

    return json.loads(result.final_output)

def retrieveMessage(message, history):
    messages = []
    for item in history:
        content = ""
        if item.get("content"):
            content = item["content"][0]["text"]
        messages.append({
            "role": item["role"],
            "content": content
        })
    messages.append({
            "role": "user",
            "content": message
        })
    
    return messages



if __name__ == "__main__":
    examples = [
        "Tell me about your background and experience.",
        "What kinds of projects are you working on now?",
        "What are your strongest technical skills?",
        "How can I get in touch with you?",
    ]
    with gr.Blocks() as demo:
        gr.ChatInterface(
            chat,
            textbox=gr.Textbox(placeholder="Ask me anything...", container=False, scale=7),
            title="Arianne's Digital Twin",
            examples=examples,
            cache_examples=True
        ).launch()
    
    demo.launch(
        theme=gr.themes.Soft(primary_hue="pink", secondary_hue="pink")
        )
