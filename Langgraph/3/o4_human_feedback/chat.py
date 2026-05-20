import os
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model
llm = init_chat_model("groq:qwen/qwen3-32b")

from typing import TypedDict
from typing_extensions import Annotated

from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
graph_builder = StateGraph(State)
memory = MemorySaver()

@tool
def human_assistance(query:str)->str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool = TavilySearch(max_results = 2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages" : [message]} 

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile(checkpointer=memory)

## view
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))

# for saving the graph image
png_data = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(png_data)

print("Graph image saved!")

user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"
config = {"configurable" : {"thread_id": "1"}}

events = graph.stream(
    {"messages": user_input},
    config,
    stream_mode="values"
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

human_response = ("We, the experts are here to help! We'd recommend you check out LangGraph to build your agent")

humman_command = Command(resume={"data" : human_response})
events = graph.stream(
   humman_command,
    config,
    stream_mode="values"
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

