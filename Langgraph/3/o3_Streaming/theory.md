In LangGraph, streaming allows you to receive graph execution results step-by-step instead of waiting for the complete execution to finish.

---

# 1. `.stream()`

```python id="x0r2ma"
graph.stream(...)
```

- Synchronous streaming method
- Returns results one-by-one while graph executes
- Used in normal Python code

Example:

```python id="8cjlwm"
for event in graph.stream(input):
    print(event)
```

Execution pauses until each step completes.

---

# 2. `.astream()`

```python id="m9hx8u"
graph.astream(...)
```

- Asynchronous version of streaming
- Used with `async/await`
- Best for FastAPI, async apps, WebSockets, real-time systems

Example:

```python id="nx31dx"
async for event in graph.astream(input):
    print(event)
```

Non-blocking execution 🚀

---

# Streaming Modes

You can control WHAT gets streamed.

---

# 3. `stream_mode="values"`

Streams the FULL graph state after every node execution.

Example:

```python id="yvjlwm"
for event in graph.stream(
    input,
    stream_mode="values"
):
    print(event)
```

Suppose state becomes:

```python id="v2utga"
{
    "messages": [
        HumanMessage(...),
        AIMessage(...)
    ]
}
```

You receive the COMPLETE updated state every time.

---

## Use case

Best when:

- you want full conversation state
- debugging
- visualizing workflow
- checkpoint inspection

---

# 4. `stream_mode="updates"`

Streams ONLY the CHANGES made by each node.

Example:

```python id="8gmsql"
for event in graph.stream(
    input,
    stream_mode="updates"
):
    print(event)
```

Instead of full state:

```python id="opzjlwm"
{
    "messages": [
        AIMessage(...)
    ]
}
```

only newly added/updated data is streamed.

---

## Use case

Best when:

- state is large
- you only care about incremental updates
- better performance
- live UI updates

---

# Overall Summary 🚀

| Method       | Type            |
| ------------ | --------------- |
| `.stream()`  | Sync streaming  |
| `.astream()` | Async streaming |

| Stream Mode | Meaning                       |
| ----------- | ----------------------------- |
| `values`    | Full state after each node    |
| `updates`   | Only node updates/differences |
