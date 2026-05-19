# Build a basic Chatbot with Langgraph (Graph API)

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages # reducers

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model

llm = ChatGroq(model="qwen/qwen3-32b")
# llm = init_chat_model("groq:qwen/qwen3-32b")

#Node functionality
# This node receives the current graph state, extracts all conversation messages, and sends them to the LLM using llm.invoke(). The model generates a response, and the node returns it inside the messages key.
# Because add_messages is used, the AI response gets appended to the existing chat history automatically.
def chatbot(state:State):
    return {"messages": [llm.invoke(state["messages"])]}

# graph
graph_builder.add_node("llmchatbot", chatbot)

graph_builder.add_edge(START, "llmchatbot")
graph_builder.add_edge("llmchatbot", END)

## compile the graph
graph = graph_builder.compile()

# ## view
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# # for saving the graph image
# png_data = graph.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")

# result = graph.invoke({"messages": "Hi"})

# # retrueve the last message and extract content from it
# print(result["messages"][-1].content)

# graph.invoke() executes the complete graph and returns the final state after execution finishes, whereas graph.stream() streams intermediate execution events step-by-step, allowing real-time monitoring of node outputs and graph progress.
for event in graph.stream({"messages": "Hi How are you?"}):
    for value in event.values():
        print(value["messages"][-1].content)