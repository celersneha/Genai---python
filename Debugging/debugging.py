from typing import Annotated
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import END, START
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
import os
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(model="qwen/qwen3-32b")

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "sample_project"

# Graph with tool call
@tool
def add(a:float,b:float):
    """Add two numbers"""
    return a+b

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

tool_node = ToolNode([add])
tools = [add]
llm_with_tool = llm.bind_tools(tools)

def call_llm_model(state:State):
    return {"messages": [llm_with_tool.invoke(state['messages'])]}

builder = StateGraph(State)
builder.add_node("tool_calling_llm", call_llm_model)
builder.add_node("tools", ToolNode(tools))

#Add edges
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", "tool_calling_llm")

graph = builder.compile()

res = graph.invoke({"messages":"What is 2+2?"})

for m in res['messages']:
    m.pretty_print()
