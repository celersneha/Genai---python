MCP stands for **Model Context Protocol**, which is an open standard used to connect AI models with external tools, APIs, databases, and services in a standardized way. It removes the need for custom integrations for every tool and allows plug-and-play communication between AI systems and external resources.

The **MCP Host** is the main AI application that the user interacts with, such as Claude Desktop, an AI IDE, or an AI agent application. Inside the host, there is an **MCP Client**, which is responsible for communicating with MCP servers using the MCP protocol.

The MCP client acts like a connector or communication layer. It:

- sends requests from the AI application
- discovers available tools
- handles structured messages
- manages request/response flow
- communicates with MCP servers over protocols like stdio, HTTP, or WebSockets

MCP clients are usually created inside the host application using MCP SDKs or libraries provided by the framework. For example, an AI application can initialize an MCP client and configure it to connect with one or multiple MCP servers.

The **MCP Server** exposes tools or resources like GitHub, databases, file systems, browsers, or APIs that the AI can use. The server receives requests from the MCP client, executes the required operation, and returns structured responses back to the AI application.

Overall flow is:

```text id="7y6kdm"
User → MCP Host → MCP Client → MCP Server → External Tool/API
```

So MCP standardizes communication between AI systems and external services, making tool integration modular, reusable, and scalable.
