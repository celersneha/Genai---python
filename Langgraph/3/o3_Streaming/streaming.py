from langgraph.checkpoint.memory import MemorySaver
from o2_ChatbotWithTool.chatbot_with_tool import llm_with_tools
from langgraph.graph import StateGraph, START, END, add_messages
from typing_extensions import Annotated
from typing import TypedDict

# run through cd Langgraph/3 > python -m o3_Streaming.streaming
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

config = {"configurable" : {"thread_id" : "1"}}

# graph_builder.invoke({"messages": "Hi, my name is Sneha and I like painting"}, config=config)

## Streaming

# for chunk in graph_builder.stream({"messages":"Hi, My name is sneha and I like painting"}, config,stream_mode="updates"):
#     print(chunk)

# Example Output:
# {
#     'Superbot': {
#         'messages': [
#             AIMessage(content='Hello Sneha! Painting is a wonderful hobby 🎨')
#         ]
#     }
# }

# for chunk in graph_builder.stream({"messages":"Hi, My name is sneha and I like painting"}, config,stream_mode="values"):
#     print(chunk)
    
# Example Output:
# {
#     'messages': [
#         HumanMessage(content='Hi, My name is sneha and I like painting'),
#         AIMessage(content='Hello Sneha! Painting is a wonderful hobby 🎨')
#     ]
# }

import asyncio

config = {
    "configurable": {
        "thread_id": "2"
    }
}

async def main():

    async for event in graph_builder.astream_events(
        {"messages": "Hi, My name is sneha and I like painting"},
        config,
        version="v2"
    ):
        print(event)

asyncio.run(main())