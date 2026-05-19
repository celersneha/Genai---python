from mcp.server.fastmcp import FastMCP

#Math is server name
mcp = FastMCP("Math")

@mcp.tool()
def add(a:int,b:int)->int:
    """Adds two numbers together.
    
    Args:
        a (int): The first number.
        b (int): The second number.
    
    Returns:
        int: The sum of the two numbers."""
    return a + b

@mcp.tool()
def multiple(a:int,b:int)->int:
    """Multiplies two numbers together.
    
    Args:
        a (int): The first number.
        b (int): The second number.
    
    Returns:
        int: The product of the two numbers."""
    return a * b

# The transport="stdio" argument tells the server to:
# use standard input/output (stdin and stdout) to receive and respond to tool function calls

if __name__=="__main__":
    mcp.run(transport="stdio")