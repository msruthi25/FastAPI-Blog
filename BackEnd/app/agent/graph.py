# graph.py
from langgraph.graph import StateGraph, END
from .state import State
from .nodes import (
    prompt_builder, createPost, extract_tool_calls, 
    arxiv_mcp_node, jsonParser, contentValidation, 
    route_after_validation, route_before_create_post,fetch_news_node
)

def build_graph():
    graph = StateGraph(State)

    # Define Nodes
    graph.add_node("promptBuilder", prompt_builder)
    graph.add_node("createPost", createPost)
    graph.add_node("extract_tool_calls", extract_tool_calls)
    graph.add_node("arxivResearch", arxiv_mcp_node)
    graph.add_node("jsonParser", jsonParser)
    graph.add_node("contentValidation", contentValidation)

    # Define Flow
    graph.set_entry_point("promptBuilder")
    graph.add_edge("promptBuilder", "createPost")
    graph.add_edge("createPost", "extract_tool_calls")

    # The Decision Point
    graph.add_conditional_edges(
        "extract_tool_calls",
        route_before_create_post,
        {
            "arxivResearch": "arxivResearch",  # Loop to tool
            "jsonParser": "jsonParser"         # Move to finishing
        }
    )

    # After research, go back to build a new prompt with the papers included
    graph.add_edge("arxivResearch", "promptBuilder")

    graph.add_edge("jsonParser", "contentValidation")

    # Validation Loop
    graph.add_conditional_edges(
        "contentValidation",
        route_after_validation,
        {
            "promptBuilder": "promptBuilder",
            "__end__": END
        }
    )

    return graph.compile()

def build_news_graph():  
    graph = StateGraph(State)

    graph.add_node("fetchNews", fetch_news_node)
    graph.add_node("promptBuilder", prompt_builder)
    graph.add_node("createPost", createPost)
    graph.add_node("extract_tool_calls", extract_tool_calls)
    graph.add_node("jsonParser", jsonParser)
    graph.add_node("contentValidation", contentValidation)

    # News flow: fetch news first then generate
    graph.set_entry_point("fetchNews")
    graph.add_edge("fetchNews", "promptBuilder")
    graph.add_edge("promptBuilder", "createPost")
    graph.add_edge("createPost", "extract_tool_calls")

    graph.add_conditional_edges(
        "extract_tool_calls",
        route_before_create_post,
        {
            "arxivResearch": "jsonParser", 
            "jsonParser": "jsonParser"
        }
    )

    graph.add_edge("jsonParser", "contentValidation")

    graph.add_conditional_edges(
        "contentValidation",
        route_after_validation,
        {
            "promptBuilder": "promptBuilder",
            "__end__": END
        }
    )

    return graph.compile()