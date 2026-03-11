from fastapi import FastAPI, HTTPException
from .schemas import ToolRequest
from .tools.search_arxiv import search_arxiv, fetch_news

app = FastAPI(title="Research MCP Server")


@app.get("/")
def health_check():
    return {"status": "MCP server running"}


@app.post("/call_tool")
def call_tool(request: ToolRequest):

    if request.tool == "search_arxiv":
        topic = request.arguments.get("topic")
        max_results = request.arguments.get("max_results", 5)

        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        return {
            "result": search_arxiv(topic, max_results)
        }
    
    if request.tool == "fetch_news":
        source = request.arguments.get("source", "hackernews")
        max_results = request.arguments.get("max_results", 5)

        return {
            "result": fetch_news(source, max_results)
        }

    raise HTTPException(status_code=404, detail=f"Tool '{request.tool}' not found")