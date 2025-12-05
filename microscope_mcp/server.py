from mcp.server.fastmcp import FastMCP
from microscope_api import Microscope

# Initialize microscope
scope = Microscope()

# MCP app
mcp = FastMCP("Microscope MCP Server")


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
    mcp.run()
