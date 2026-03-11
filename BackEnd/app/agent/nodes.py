import json
from .state import State
from langgraph.graph import END
from .llm import call_llm
from mcp_server.tools.search_arxiv import search_arxiv
from mcp_server.tools.fetch_news import fetch_news
import requests
import random

# --- Node 1: Prompt Builder ---
def prompt_builder(state: State) -> State:    
    # Safety break
    attempt_count = state.get("attempt_count", 0)
    if attempt_count >= 5:
        return END
    state["attempt_count"] = attempt_count + 1

    research_papers = state.get("research_papers", [])
    validation_errors = state.get("validation_errors", [])
    
    user_input_obj = state.get("topic", "")
    user_input_text = getattr(user_input_obj, "topic", str(user_input_obj)).strip()

    if "Image context:" in user_input_text:
        input_type = "image"
    elif "Document content:" in user_input_text:
        input_type = "document"
    elif user_input_text.lower().startswith("http://") or user_input_text.lower().startswith("https://"):
        input_type = "url"
    else:
        input_type = "text"

    # STEP 1: Handle Validation Retries
    if validation_errors:
        errors = "\n".join(validation_errors)
        state["prompt"] = (
            f"Your previous JSON output was invalid.\n"
            f"Errors:\n{errors}\n\n"
            "Please regenerate the JSON strictly with this exact structure:\n"
            "{\n"
            '  "Title": string,\n'
            '  "Content": string (minimum 200 words),\n'
            '  "img_url": string\n'
            "}\n\n"
            "Requirements:\n"
            "-give an working img_url related to topic\n"
            "- Use research papers if available, summarize in your own words\n"
            "- Include introduction, 3-5 sections with headings, and conclusion\n"
            "- Do NOT include explanations or markdown outside JSON"
        )
        return state

    # STEP 2: Topic-only (no research yet)
    # URL input
    if input_type == "url" and not research_papers:
        state["prompt"] = (
            f"You are a professional blog writer.\n\n"
            f"The user has provided a URL to reference:\n{user_input_text}\n\n"
            "Requirements:\n"
            "- Content must be at least 200 words\n"
            "- Return ONLY valid JSON:\n"
            "{\n"
            '  "Title": string,\n'
            '  "Content": string,\n'
            '  "img_url": string\n'
            "}\n"
            "-give an working img_url related to topic.\n"
            "- Summarize or rewrite content from the URL in your own words\n"
            "- Include introduction, 3-5 sections with headings, and conclusion\n"
            "- Return ONLY valid JSON: Title, Content, img_url"
        )
        return state
     
    # Image input
    if input_type == "image" and not research_papers:
        state["prompt"] = (
            f"You are a professional blog writer.\n\n"
            f"The user has provided an image with the following context:\n{user_input_text}\n\n"
            "Requirements:\n"
            "- Write a blog post inspired by the image\n"
            "- Content must be at least 200 words\n"
            "- Return ONLY valid JSON:\n"
            "{\n"
            '  "Title": string,\n'
            '  "Content": string,\n'
            '  "img_url": string\n'
            "}\n"
            "- give a working img_url related to the image topic\n"
            "- Include introduction, 3-5 sections with headings, and conclusion\n"
            "- Return ONLY valid JSON: Title, Content, img_url"
        )
        return state
    
    # News input
    news_items = state.get("news_items", [])
    if news_items and not research_papers:
        news_text = "\n".join([
            f"- Title: {item['title']}\n  URL: {item['url']}\n  Summary: {item['summary']}"
            for item in news_items
        ])
        state["prompt"] = (
            f"You are a professional tech blog writer.\n\n"
            f"Based on this tech news story:\n{news_text}\n\n"
            "Requirements:\n"
            "- Write an engaging blog post about this news\n"
            "- Content must be at least 200 words\n"
            "- Include introduction, 3-5 sections with headings, and conclusion\n"
            "- give a working img_url related to the topic\n"
            "- Return ONLY valid JSON:\n"
            "{\n"
            '  "Title": string,\n'
            '  "Content": string,\n'
            '  "img_url": string\n'
            "}\n"
            "- Format content using Markdown (use ## for headings, **bold** for emphasis)\n"
            "- Do NOT use HTML tags\n"
            "- Return ONLY valid JSON\n"
        )
        return state

    # Document input
    if input_type == "document" and not research_papers:
        state["prompt"] = (
            f"You are a professional blog writer.\n\n"
            f"The user has provided a document with the following content:\n{user_input_text}\n\n"
            "Requirements:\n"
            "- Write a blog post based on the document content\n"
            "- Content must be at least 200 words\n"
            "- Return ONLY valid JSON:\n"
            "{\n"
            '  "Title": string,\n'
            '  "Content": string,\n'
            '  "img_url": string\n'
            "}\n"
            "- give a working img_url related to the document topic\n"
            "- Include introduction, 3-5 sections with headings, and conclusion\n"
            "- Return ONLY valid JSON: Title, Content, img_url"
        )
        return state

    # Topic 
    if not research_papers:
        state["prompt"] = (
            f"You are a professional blog writer.\n\n"
            f"Topic: {user_input_text}\n\n"
            "Requirements:\n"
            "- Content must be at least 200 words\n"
            "- Return ONLY valid JSON:\n"
            "{\n"
            '  "Title": string,\n'
            '  "Content": string,\n'
            '  "img_url": string\n'
            "}\n"
            "-give an working img_url related to topic.\n"
            "- No research papers available; write from general knowledge\n"
            "- Include introduction, 3-5 sections with headings, and conclusion\n"
            "- Return ONLY valid JSON: Title, Content, img_url"
        )
        return state

    # STEP 3: With research
    papers_text = "\n".join([f"- {p.get('title')}: {p.get('summary')}" for p in research_papers])
    state["prompt"] = (
        f"You are a professional tech blog writer.\n\n"
        f"Topic: {state['topic']}\n"
        "Use the following research papers as references (do NOT copy text verbatim):\n"
        f"{papers_text}\n\n"
        "Requirements:\n"
        "- Write an engaging blog post in your own words\n"
        "- Include introduction, 3-5 sections with headings, and conclusion\n"
        "- Content must be at least 200 words\n"
        "- Return ONLY valid JSON:\n"
        "-give an working img_url related to topic\n"
        "{\n"
        '  "Title": string,\n'
        '  "Content": string,\n'
        '  "img_url": string\n'
        "}\n"
        "- Do NOT include any markdown outside JSON"
    )
    return state

# --- Node 2: Call LLM ---
def createPost(state: State) -> dict:
    """Calls the LLM with the generated prompt."""    
    try:
        response = call_llm(state.get("prompt", ""))
        state["response"] = response 
        state["raw_data"] = response  
    except Exception as e:
        print(f"LLM Error: {e}")
        state["response"] = ""
        state["raw_data"] = ""
    
    return state

# --- Node 3: Tool Call Extractor ---
def extract_tool_calls(state: State) -> dict:
    """Checks if the LLM output is a request for a tool or the final content."""
    try:
        raw_content = state.get("raw_data", "")
        # Handle cases where LLM wraps JSON in markdown blocks
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_json)
        
        # Check if the LLM explicitly requested the search tool
        tool_calls = parsed.get("tool_calls", [])
        return {"tool_calls": tool_calls}
    except Exception:
        return {"tool_calls": []}

# --- Node 4: MCP Arxiv Node ---
def arxiv_mcp_node(state: State) -> State:
    """Executes the actual Arxiv search via MCP."""
    topic = state.get("topic")
    print(f"--- FETCHING RESEARCH FOR: {topic} ---")
    
    try:
        # Assuming search_arxiv returns a dict with a 'papers' list
        response = search_arxiv(topic, max_results=3)
        print(response)
        state["research_papers"] = response.get("papers", [])
    except Exception as e:
        print(f"Arxiv Error: {e}")
        state["research_papers"] = []
    
    return state

# --- Node 5: JSON Parser ---
def jsonParser(state: State) -> dict:
    """Parses the final blog content into state fields."""
    try:
        raw_content = state.get("raw_data", "")
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        return {
            "title": data.get("Title") or data.get("title"),
            "content": data.get("Content") or data.get("content"),
            "img_url": data.get("img_url")
        }
    except Exception as e:
        return {"validation_errors": [f"JSON Parsing failed: {str(e)}"]}

# --- Node 6: Content Validation ---
def contentValidation(state: State) -> State:
    """Validates the blog against requirements."""
    errors = []
    
    if not state.get("title"):
        errors.append("Title is missing.")
    
    content = state.get("content", "")
    print(content)
    if not content:
        errors.append("Content is missing.")
    elif len(content.split()) < 200:
        errors.append(f"Content is too short ({len(content.split())} words). Need 200.")
    
    if not state.get("img_url"):
        errors.append("Image URL is missing.")

    state["is_valid"] = len(errors) == 0
    state["validation_errors"] = errors
    return state

# --- Routing Logic ---

def route_before_create_post(state: State):
    """Routes to research node or parser node based on tool_calls."""
    if "search_arxiv" in state.get("tool_calls", []):
        return "arxivResearch"
    return "jsonParser"

def route_after_validation(state: State):
    """Routes back to prompt builder if invalid, otherwise finishes."""
    if state.get("validation_errors"):
        return "promptBuilder"
    return END


# --- Node 7: Fetch News Node ---
def fetch_news_node(state: State) -> State:
    """Fetches latest tech news from RSS feed."""
    source = state.get("news_source", "hackernews")
    print(f"--- FETCHING NEWS FROM: {source} ---")

    try:
        response = fetch_news(source=source, max_results=5)
        articles = response.get("articles", [])
        print(f"Fetched {len(articles)} articles")
        state["news_items"] = articles
    except Exception as e:
        print(f"News Fetch Error: {e}")
        state["news_items"] = []

    return state