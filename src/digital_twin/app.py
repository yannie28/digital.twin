import asyncio
from agents import Agent, Runner, trace, function_tool, SQLiteSession
from dotenv import load_dotenv
import gradio as gr
from digital_twin.styles import custom_css
from digital_twin.context import TWIN_SYSTEM_PROMPT
from tools.notification_tool import record_user_details, record_unknown_question


load_dotenv(override=True)

async def chat(message, history):
    tools=[record_user_details, record_unknown_question]
    agent = Agent(name="Arianne's Digital Twin", instructions=TWIN_SYSTEM_PROMPT, model="gpt-5.4-mini", tools=tools)
    result = await Runner.run(agent, message)
    print(result.final_output)
    return result.final_output

if __name__ == "__main__":
    gr.ChatInterface(chat).launch(inbrowser=True)

# if __name__ == "__main__":
#     with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
#         gr.Markdown(
#             """
#             # 💖 Arianne's Digital Twin
#             ### Talk to my digital twin about my career
#             """
#         )

#         chatbot = gr.ChatInterface(
#             fn=chat,
#             chatbot=gr.Chatbot(height=500),
#             textbox=gr.Textbox(
#                 placeholder="Type your message here... 💌",
#                 lines=1,
#             ),
#         )

#     demo.launch()