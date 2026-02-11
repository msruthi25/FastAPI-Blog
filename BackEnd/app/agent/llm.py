from openrouter import OpenRouter
from .state import State

client = OpenRouter(api_key="Add your API Key")

def call_llm(state:State) ->str:
    response = client.chat.send(
      model ="openai/gpt-4o-mini",
      messages=[{"role":"system",
                 "content":state["prompt"]}]
    )
    return response