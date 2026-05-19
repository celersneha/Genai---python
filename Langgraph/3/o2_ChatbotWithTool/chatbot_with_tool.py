#this follows ReAct architecture

import os
from dotenv import load_dotenv
load_dotenv()
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq

tool = TavilySearch(max_results=2)
# print(tool.invoke("What is langgraph?"))
llm = ChatGroq(model="qwen/qwen3-32b")

# ## custom func
# Docstrings are very important when creating tools for LLMs because the LLM uses them to understand:

# what the tool does
# what inputs it expects
# what output it returns

def multiply_num(a:int, b:int)->int:
    """
    Multiply a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: output int
    """
    return a*b

tools = [tool, multiply_num]
llm_with_tools = llm.bind_tools(tools)

#StateGraph
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from typing import TypedDict
from langgraph.graph import add_messages
from typing_extensions import Annotated
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
memory = MemorySaver()

def tool_calling_llm(state:State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder = StateGraph(State)

builder.add_node("tool_calling_llm" , tool_calling_llm )
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm" , tools_condition)
builder.add_edge("tools", "tool_calling_llm")

graph = builder.compile(checkpointer=memory)

# ## view
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# # for saving the graph image
# png_data = graph.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")

# res = graph.invoke({"messages":"What is the weather today in Indore and then tell me what is 5*2?"})

# # print(res["messages"][-1])
# for m in res["messages"]:
#     m.pretty_print()
if __name__ == "__main__":
    config={"configurable":{"thread_id":"1"}}

    res = graph.invoke({"messages":"Hi my name is Sneha"}, config=config)
    # print(res["messages"][-1])
    for m in res["messages"]:
        m.pretty_print()

    res = graph.invoke({"messages":"Hi can you please tell me my name"}, config=config)
    # print(res["messages"][-1])
    for m in res["messages"]:
        m.pretty_print()
