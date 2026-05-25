import os
from typing import TypedDict, Annotated, List, Literal
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langchain.messages import SystemMessage

from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


# State
class AgentState(MessagesState):
    next_agent:str # which agent should go next
    
# create simple tool
@tool
def search_web(query:str)->str:
    """For searching the web"""
    search = TavilySearchResults(max_results=3)
    results=search.invoke(query)
    return str(results)

@tool
def write_summary(content:str)->str:
    """Write a summary of the provided content."""
    # simple summary generation
    summary = f"Summary of findings:\n\n{content[:500]}"
    return summary

llm = ChatGroq(model="qwen/qwen3-32b")

# Define agent functions (simpler approach)
def researcher_agent(state:AgentState):
    """Researcher agent that searches for information"""
    
    messages = state["messages"]
    
    # Add system msg for context
    system_msg = SystemMessage(content="You are a research assistant. Use the search_web tool to find information about the user's request.")
    
    researcher_llm= llm.bind_tools([search_web])
    response = researcher_llm.invoke([system_msg] + messages)
    
    return {
        "messages" : [response],
        "next_agent" : "writer"
    }
    
def writer_agent(state: AgentState):
    """Writer agent that creates summaries"""
    
    messages = state["messages"]
    system_msg = SystemMessage(content="You are a technical writer. Review the conversation and create  a clear, concise summary of the findings.")
    
    writer_llm = llm.bind_tools([write_summary])
    response = writer_llm.invoke([system_msg] + messages)
    
    return {
        "messages": [response],
        "next_agent":"end"
    }
    
# Tool executor node
def execute_tools(state:AgentState):
    """Execute any pending tool calls"""
    messages = state["messages"]
    last_msg = messages[-1]
    
    # check if there are tool calls to execute
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        # create tool node and execute
        tool_node=ToolNode([search_web, write_summary])
        response = tool_node.invoke(state)
        return response
    
    return state

workflow = StateGraph(AgentState)

workflow.add_node("researcher", researcher_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("tools", execute_tools)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "tools")
workflow.add_edge("tools", "writer")
workflow.add_edge("writer", END)
final_workflow = workflow.compile()
# # ## view
# from IPython.display import Image, display
# display(Image(final_workflow.get_graph().draw_mermaid_png()))

# # for saving the graph image
# png_data = final_workflow.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")
response = final_workflow.invoke({"messages": "Research about the usecase of agentic ai in business"})

print(response["messages"][-1].content)