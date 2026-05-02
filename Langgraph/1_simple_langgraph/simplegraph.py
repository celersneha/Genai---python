from typing_extensions import TypedDict
import random
from typing import Literal
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
# represents the input and output structure from a node
class State(TypedDict):
    graph_info: str
    
# here the return statements appends the value of original state with the latest updation and returns the variable of state, i.e., graph_info
# node 1 
def start_play(state: State):
    print("Start Play node has been called")
    return {"graph_info" : state["graph_info"] + "I am planning to play"}

# node 2
def cricket(state: State):
    print("Cricket node has been called")
    return {"graph_info" : state["graph_info"] + "Cricket"}

# node 3
def badminton(state: State):
    print("Badminton node has been called")
    return {"graph_info" : state["graph_info"] + "Badminton"}

# This tells LangGraph:
# next node can ONLY be:
# "cricket"
# "badminton"
def random_play(state:State) -> Literal['cricket','badminton']:
    if random.random()>0.5:
        return "cricket"
    else:
        return "badminton"
    
## Build Graph

graph = StateGraph(State)

## add all the nodes
## first parameter - node_name
## second parameter - func_name
graph.add_node("start_play", start_play)
graph.add_node("cricket", cricket)
graph.add_node("badminton", badminton)

## Schedule the flow of the graph
graph.add_edge(START, "start_play")
graph.add_conditional_edges("start_play", random_play)
graph.add_edge("cricket", END)
graph.add_edge("badminton", END)

## Compile the graph
# What Happens Internally During Compile?
# LangGraph typically:
# validates nodes
# validates edges
# checks missing paths
# builds execution DAG/workflow
# prepares runtime state handling
# optimizes traversal logic

#Compiled graph/app is the runnable object.
graph_builder = graph.compile()

## view
# display(Image(graph_builder.get_graph().draw_mermaid_png()))

# for saving the graph image
# png_data = graph_builder.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")

graph_builder.invoke({"graph_info" : "My name is Sneha"})