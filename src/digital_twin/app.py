import asyncio
from agents import Agent, Runner, trace, function_tool, SQLiteSession
from dotenv import load_dotenv
import gradio as gr
from digital_twin.context import TWIN_SYSTEM_PROMPT
from tools.notification_tool import record_user_details, record_unknown_question


load_dotenv(override=True)

async def chat(message, history):
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

    agent = Agent(
        name="Arianne's Digital Twin",
        instructions=TWIN_SYSTEM_PROMPT,
        model="gpt-5.4-mini"
    )
    result = await Runner.run(agent, messages)
    return result.final_output

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
        )
    
    demo.launch(
        theme=gr.themes.Soft(primary_hue="pink", secondary_hue="pink")
        )
