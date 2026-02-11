from openrouter import OpenRouter
from .state import State

client = OpenRouter(api_key="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")

def call_llm(state:State) ->str:
    response = client.chat.send(
      model ="openai/gpt-4o-mini",
      messages=[{"role":"system",
                 "content":state["prompt"]}]
    )
    return response