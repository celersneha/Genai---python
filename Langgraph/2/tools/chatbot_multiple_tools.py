## tools

from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper


api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
arxiv= ArxivQueryRun(api_wrapper=api_wrapper_arxiv, description="Query Arxiv Paper")
print(arxiv.name)

# result = arxiv.invoke("Attention is all you need")
# print(result)

api_wrapper_wikipedia = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
wikipedia= WikipediaQueryRun(api_wrapper=api_wrapper_wikipedia, description="Query Wikipedia")
print(wikipedia.name)

# result = wikipedia.invoke("langchain")
# print(result)

from dotenv import load_dotenv
load_dotenv()
import os

os.environ["TAVILY_API_KEY"]=os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from langchain_tavily import TavilySearch

tavily = TavilySearch()

# print(tavily.invoke("Provide me the recent AI news"))

## combine all these tools in the list

tools = [arxiv, wikipedia, tavily]

# initialize llm model

from langchain_groq import ChatGroq

llm = ChatGroq(model="qwen/qwen3-32b")

# result = llm.invoke("What is ai?")
# print(result.content)

llm_with_tools = llm.bind_tools(tools=tools)

# result = llm_with_tools.invoke("What is the recent news on AI?")
# print(result)

## workflow
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, HumanMessage # human message or AI message
from typing import Annotated #labelling
from langgraph.graph.message import add_messages # reducers in langgraph

# State is a TypedDict representing the graph state. 
# `messages` stores a list of LangChain messages (HumanMessage, AIMessage, etc.).
# `Annotated[..., add_messages]` attaches the `add_messages` reducer, which tells
# LangGraph to append/merge new messages into the existing list instead of overwriting them,
# helping maintain conversation history across the workflow.s
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

# node definitions
def tool_calling_llm(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# build graph
builder = StateGraph(State)
builder.add_node("tool_calling_llm" , tool_calling_llm)
builder.add_node("tools" , ToolNode(tools))

# add edges
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm",
## If the latest assistant message is a tool call → route to tools
# Otherwise → continue the normal conversation flow
tools_condition)
builder.add_edge("tools", "tool_calling_llm")

graph = builder.compile()
# ## view
# display(Image(graph.get_graph().draw_mermaid_png()))

# # for saving the graph image
# png_data = graph.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")

messages = graph.invoke({"messages" : HumanMessage(content="What is recent AI news?? and then I want to know info about latest research paper on AI.")})
for m in messages['messages']:
    m.pretty_print()