from mcp.server.fastmcp import FastMCP
from microscope_api import Microscope

# Initialize microscope
scope = Microscope()

# MCP app
mcp = FastMCP("Microscope MCP")


@mcp.tool()
def snap_image():
    """Capture an image from the microscope."""
    return scope.snap_image()


@mcp.tool()
def move_stage(x: float, y: float, z: float):
    """Move microscope stage to (x,y,z)"""
    return scope.move_stage(x, y, z)


@mcp.tool()
def get_stage_position():
    """Return current stage position"""
    return scope.get_stage_position()


if __name__ == "__main__":

    # as STDIO
    mcp.run()

    ## as network MCP server
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=4200, path="/mcp")
    # or async version
    # import asyncio
    # async def main():
    #     await mcp.run_streamable_http_async(host="127.0.0.1", port=4200)
    # asyncio.run(main())
