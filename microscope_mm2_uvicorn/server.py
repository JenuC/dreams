from mcp.server.fastmcp import FastMCP
from microscope_api import RealMicroscope

scope = RealMicroscope()
mcp = FastMCP("Microscope MCP (Real)", host="127.0.0.1", port=4201)


# --- Tools ---

@mcp.tool()
def snap_image() -> dict:
    """Capture an image from the microscope at the current stage position."""
    return scope.snap_image()


@mcp.tool()
def move_stage(x: float, y: float, z: float) -> dict:
    """Move the microscope stage to the given (x, y, z) coordinates in µm."""
    return scope.move_stage(x, y, z)


@mcp.tool()
def get_stage_position() -> dict:
    """Return the current stage position as {x, y, z}."""
    return scope.get_stage_position()


@mcp.tool()
def wait(seconds: float) -> dict:
    """Pause execution for the given number of seconds."""
    return scope.wait(seconds)


# --- Resources ---

@mcp.resource("microscope://latest_image", mime_type="image/png")
def latest_image() -> bytes:
    """The most recently captured image as a PNG."""
    return scope.get_image_png()


# --- Prompts ---

@mcp.prompt()
def tile_scan_xy(
    x_positions: list[float],
    y_positions: list[float],
    z: float,
    delay_seconds: float = 1.0,
) -> str:
    """Generate a prompt to run a 2D tile scan at fixed Z with a delay between tiles."""
    return f"""
You are controlling a microscope via MCP tools.

Run a tiled XY acquisition:
- Fixed Z = {z}
- Delay between tiles = {delay_seconds}s
- X positions: {x_positions}
- Y positions: {y_positions}

For each y in Y positions, for each x in X positions:
  1. Call move_stage(x=x, y=y, z={z})
  2. Call snap_image()
  3. Call wait(seconds={delay_seconds})

Do not skip any positions. Report progress after each tile.
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        mcp.streamable_http_app(),
        host="127.0.0.1",
        port=4201,
        timeout_graceful_shutdown=0,
    )
