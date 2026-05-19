- **State** → The shared data structure of the graph that stores information and gets passed between nodes. Each node can read and update this state.

- **Nodes** → The execution units of the graph, usually Python functions, that perform tasks like LLM calls, tool usage, calculations, or decision-making using the current state.

- **Edges** → The connections between nodes that define the workflow and decide which node executes next, either directly or conditionally.

`add_messages` is used in LangGraph to automatically manage and append chat messages inside the graph state.

Here’s what happens 👇

---

## What `add_messages` does

Normally, when a node returns a value, it replaces the old state value.

But with `add_messages`:

```python
{"messages": [AIMessage(content="Hello")]}
```

does NOT overwrite previous messages.

Instead, it automatically appends/merges them into the existing message list.

So:

```python
Old:
[HumanMessage("Hi")]

New:
[AIMessage("Hello")]
```

becomes:

```python
[
  HumanMessage("Hi"),
  AIMessage("Hello")
]
```

---

## How messages are stored

Messages are stored inside the graph **state dictionary** under the `messages` key.

Internally it looks something like:

```python
state = {
    "messages": [
        HumanMessage(content="Hi"),
        AIMessage(content="Hello")
    ]
}
```

These are actual LangChain message objects:

- `HumanMessage`
- `AIMessage`
- `SystemMessage`
- `ToolMessage`

---

## Where are they stored?

By default:

- messages are stored **in memory during graph execution**
- they exist inside the graph state object

This means:

- temporary storage
- lost after execution ends

---

## Persistent storage (optional)

If you use:

- `MemorySaver`
- checkpointers
- databases

then LangGraph can persist state/messages.

Example:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph.compile(checkpointer=memory)
```

Now conversation history gets stored across runs using a thread/session ID.

You can also store them in:

- SQLite
- Postgres
- Redis
- custom databases

depending on the checkpointer used.

---

## Why `Annotated[..., add_messages]` is needed

This tells LangGraph:

> “For this field, merge messages intelligently instead of replacing them.”

Without it:

```python
messages = new_messages
```

With it:

```python
messages += new_messages
```

So it behaves like chat history automatically 💬

**Interview Answer**
`add_messages` only controls how messages are updated in the graph state. It appends new messages to the existing message list instead of overwriting them. However, it does not provide permanent memory storage. By default, messages are stored only in the in-memory state during the current execution of the Python program. So if the program is run again, the previous conversation history is lost. To persist messages across executions, LangGraph requires a checkpointer or memory backend such as `MemorySaver`, SQLite, Postgres, or Redis.
