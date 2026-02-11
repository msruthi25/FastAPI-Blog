from .nodes import prompt_builder, jsonParser, contentValidation, route_after_validation,createPost
from langgraph.graph import StateGraph
from .state import State

def build_graph():
    graph=StateGraph(State)
    graph.add_node("promptBuilder",prompt_builder)
    graph.add_node("createPost",createPost)
    graph.add_node("jsonParser",jsonParser)
    graph.add_node("contentValidation",contentValidation)

    graph.add_edge("promptBuilder","createPost")
    graph.add_edge("createPost","jsonParser")
    graph.add_edge("jsonParser","contentValidation")

    graph.add_conditional_edges("contentValidation",route_after_validation)

    graph.set_entry_point("promptBuilder")
    return graph.compile()