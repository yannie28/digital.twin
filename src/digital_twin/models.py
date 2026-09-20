import asyncio
import os
from agents import Agent, OpenAIChatCompletionsModel, Runner
from openai import AsyncOpenAI, InternalServerError, NotFoundError, RateLimitError

GPT_MODEL = "gpt-5.6-luna"
GEMINI_MODELS = ("gemini-3.8-flash", "gemini-3.6-flash")
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

def gemini_chat_model(model_name):
    return OpenAIChatCompletionsModel(model=model_name, openai_client=gemini_client)

async def run_gemini_agent(*, name, instructions, output_type, messages):
    last_error = None
    for model_name in GEMINI_MODELS:
        agent = Agent(
            name=name,
            instructions=instructions,
            model=gemini_chat_model(model_name),
            output_type=output_type,
        )
        for attempt in range(2):
            try:
                return await Runner.run(agent, messages)
            except NotFoundError as exc:
                last_error = exc
                break
            except (RateLimitError, InternalServerError) as exc:
                last_error = exc
                if attempt == 0:
                    await asyncio.sleep(2)
                    continue
                break
    raise last_error

async def run_gpt_agent(*, name, instructions, output_type, messages):
    agent = Agent(
        name=name,
        instructions=instructions,
        model=GPT_MODEL,
        output_type=output_type,
    )
    return await Runner.run(agent, messages)