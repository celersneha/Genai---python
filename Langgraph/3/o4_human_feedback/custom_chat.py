import argparse
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from typing import TypedDict
from typing_extensions import Annotated

load_dotenv()


class State(TypedDict):
	messages: Annotated[list, add_messages]


def build_graph(checkpointer: SqliteSaver):
	llm = init_chat_model("groq:qwen/qwen3-32b")

	tool = TavilySearch(max_results=2)
	tools = [tool]
	llm_with_tools = llm.bind_tools(tools)

	def chatbot(state: State):
		message = llm_with_tools.invoke(state["messages"])
		return {"messages": [message]}

	graph_builder = StateGraph(State)
	graph_builder.add_node("chatbot", chatbot)

	tool_node = ToolNode(tools)
	graph_builder.add_node("tools", tool_node)

	graph_builder.add_edge(START, "chatbot")
	graph_builder.add_conditional_edges("chatbot", tools_condition)
	graph_builder.add_edge("tools", "chatbot")

	return graph_builder.compile(checkpointer=checkpointer)


def run_stream(graph, payload, config):
	events = graph.stream(payload, config, stream_mode="values")
	for event in events:
		if "messages" in event and event["messages"]:
			event["messages"][-1].pretty_print()


def main():
	parser = argparse.ArgumentParser(description="LangGraph Tavily CLI")
	parser.add_argument(
		"--db",
		default=".langgraph_checkpoints.sqlite",
		help="SQLite file for checkpoints",
	)
	parser.add_argument("--thread-id", default="1", help="Thread ID")

	args = parser.parse_args()

	db_path = Path(args.db).expanduser()
	if not db_path.is_absolute():
		db_path = (Path(__file__).parent / db_path).resolve()
	db_path.parent.mkdir(parents=True, exist_ok=True)
	config = {"configurable": {"thread_id": args.thread_id}}
	with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
		graph = build_graph(checkpointer)
		while True:
			next_input = input("\nWhat do you need help with? (or type 'exit'): ").strip()
			if next_input.lower() in ("exit", "quit"):
				break
			call_state = {"messages": [HumanMessage(next_input)]}
			run_stream(graph, call_state, config)


if __name__ == "__main__":
	main()
