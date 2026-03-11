from openrouter import OpenRouter
from .state import State
import asyncio
from functools import partial
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyse_image_llm(image_base64: str, media_type: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{media_type};base64,{image_base64}"}
                },
                {
                    "type": "text",
                    "text": "Briefly analyse this image in 2-3 sentences. Describe the main subject, mood and context for a blog post."
                }
            ]
        }]
    )
    return response.choices[0].message.content


# ✅ Async wrappers
async def call_llm_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(call_llm, prompt)
    )


async def analyse_image_llm_async(image_base64: str, media_type: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(analyse_image_llm, image_base64, media_type)
    )