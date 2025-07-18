from mcp.server.fastmcp import FastMCP
import inspect

mcp = FastMCP(name="microscope-server", version="0.1.0")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Return the sum of two numbers."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
