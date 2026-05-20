- `init_chat_model()` initializes the LLM which performs reasoning and tool calling.

- `State(TypedDict)` with `add_messages` stores conversation history inside graph state.

- `MemorySaver()` acts as a checkpointer so graph state can be saved and resumed after interruption.

- `@tool` creates the `human_assistance` tool which the LLM can call.

- `interrupt({"query": query})` pauses graph execution and waits for external human input.

- `llm.bind_tools(tools)` binds Tavily Search and human assistance tools with the LLM.

- `chatbot()` node sends conversation history to the LLM and gets either:
  - direct response
  - or tool call request.

- `ToolNode(tools)` executes the tools requested by the LLM.

- `tools_condition` checks whether the LLM requested any tool call.

- `graph_builder.add_edge("tools", "chatbot")` creates the ReAct loop:

```text id="r1"
Reason → Tool Call → Observe Result → Reason Again
```

- `graph.compile(checkpointer=memory)` compiles the graph with checkpointing support.

- `graph.stream()` starts graph execution with the user query.

- If the LLM decides human help is needed, it calls `human_assistance()`.

- `interrupt()` pauses execution and saves checkpoint state.

- `Command(resume={"data": human_response})` resumes graph execution with human feedback.

- The human response is injected back into the tool, returned to the LLM, and the LLM generates the final answer.

**Human Assistance tool**

- `@tool` converts the normal Python function into a LangChain-compatible tool. This allows the LLM to understand the tool’s purpose, generate arguments automatically, and invoke it whenever required during reasoning.

- `def human_assistance(query:str)->str` defines a custom tool that accepts a query string and returns a string response. The query usually contains the problem or request for which the AI needs human intervention.

- The docstring `"Request assistance from a human."` acts as a natural language description for the LLM. During tool selection, the model reads this description to understand:
  - what the tool does
  - when it should be used
  - what kind of input it expects

- `interrupt({"query": query})` is the core Human-in-the-Loop feature in LangGraph. When this line executes:
  - graph execution pauses immediately
  - current graph state and checkpoint are saved
  - control exits the graph temporarily
  - the graph waits for external human input before continuing

- The payload:

```text id="d1"
{"query": query}
```

contains the information that should be shown to the human. This allows external systems, supervisors, or users to understand what assistance is required.

- Since execution is paused, checkpointing is necessary. `MemorySaver` or another checkpointer stores the graph state so execution can later resume from the exact interruption point instead of restarting the workflow.

- Later, the graph is resumed using:

```text id="d2"
Command(resume={"data": human_response})
```

This sends external human feedback back into the interrupted graph execution.

- The resumed response gets injected into:

```text id="d3"
human_response
```

So internally, the tool now receives the actual human-provided answer.

- `return human_response["data"]` returns the human feedback as the tool output. LangGraph automatically converts this into a `ToolMessage` and appends it to the graph state.

- The updated conversation history is then sent back to the LLM. The model observes:
  - original user query
  - tool call
  - human response/tool output

  and continues reasoning to generate the final response.

- This pattern enables advanced Human-in-the-Loop workflows where AI systems can escalate tasks to humans whenever:
  - expert approval is needed
  - confidence is low
  - sensitive decisions are involved
  - manual verification is required
  - enterprise escalation workflows are necessary.
