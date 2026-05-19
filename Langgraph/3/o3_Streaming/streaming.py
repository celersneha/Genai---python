from langgraph.checkpoint.memory import MemorySaver
from o2_ChatbotWithTool.chatbot_with_tool import llm_with_tools
from langgraph.graph import StateGraph, START, END, add_messages
from typing_extensions import Annotated
from typing import TypedDict


memory = MemorySaver()

class State(TypedDict):
    messages: Annotated[list, add_messages]

def superbot(state:State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph =StateGraph(State)

graph.add_node("Superbot", superbot)

graph.add_edge(START, "Superbot")
graph.add_edge("Superbot", END)

graph_builder = graph.compile(checkpointer=memory)

# ## view
# from IPython.display import Image, display
# display(Image(graph_builder.get_graph().draw_mermaid_png()))

# # for saving the graph image
# png_data = graph_builder.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")
