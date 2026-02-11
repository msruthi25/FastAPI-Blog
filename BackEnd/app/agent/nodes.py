from .state import State
from langgraph.graph import StateGraph,END
import json
from .llm import call_llm

#Prompt Builder
def prompt_builder(state: State) -> State:
  if state.get("attempt_count", 0) < 3:
    state["attempt_count"] = state.get("attempt_count", 0) + 1
    if not state.get("validation_errors"):
        state["prompt"] = (
            f"You are a tech blog writer.\n"
            f"Write a blog on: {state['topic']}\n"
            f"Return only JSON with keys: Title, Content, img_url related to the topic which works\n"
            f"For img_url follow this:"
            f"- Search Wikimedia Commons for an image related to the topic.\n"
            f" - Return ONLY the direct image URL (ending with .jpg, .png, .jpeg, .webp, etc.)."
            f"- The URL must be valid and publicly accessible."
            f"- Do not return any HTML, markdown, or extra text."
            f"The content must be at least 200 words (>= 200 words).\n"
            f"No extra text."
        )
    else:
        errors = "\n".join(state["validation_errors"])
        state["prompt"] = (
            "Your previous blog failed validation.\n"
            f"Errors:\n{errors}\n\n"
            f"Here is the previous output:\n"
            f"Title: {state.get('title')}\n"
            f"Content: {state.get('content')}\n\n"
            f"img_url:{state.get('img_url')}\n\n"
            f"For img_url follow this:"
            f"- Search Wikimedia Commons for an image related to the topic.\n"
            f" - Return ONLY the direct image URL (ending with .jpg, .png, .jpeg, .webp, etc.)."
            f"- The URL must be valid and publicly accessible."
            f"- Do not return any HTML, markdown, or extra text."
            "Regenerate the blog fixing all errors.\n"
            "Return only JSON with keys: Title, Content, img_url related to the topic which works\n"
            "The content must be at least 200 words (>= 200 words)."
        )
  else:
     return END
  return state


#Create Post/Call LLM
def createPost(state:State) -> str:
  response = call_llm(state)
  data = response.choices[0].message.content
  return {"raw_data":data}


#Json Parser
def jsonParser(state:State) -> State:
  data = json.loads(state.get("raw_data"))
  return {"title":data.get("Title"),"content":data.get("Content"),"img_url":data.get("img_url")}

#Validating Content
def contentValidation(state:State):
  state["is_valid"] = True 
  state["validation_errors"] = [] 
  if not state.get("title"):
    state["is_valid"] = False
    state["validation_errors"].append("Title is empty")
  if not state.get("content"):
    state["is_valid"] = False
    state["validation_errors"].append("Content is empty")
  if not state.get("img_url"):
    state["is_valid"] = False
    state["validation_errors"].append("Image URL is empty")
  if len(state["content"].split()) < 200:    
    state["is_valid"] = False
    state["validation_errors"].append("Content is less than 200 words")
  return state

#Router 
def route_after_validation(state: State):
    if state["validation_errors"]:
      print(state)
      return "promptBuilder"
    return END