from mcp.server.fastmcp import FastMCP
from microscope_api import Microscope
import io
from PIL import Image
import numpy as np

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


@mcp.tool()
def wait(seconds: float):
    return scope.wait(seconds)


# @mcp.resource("microscope://latest_image")
# def latest_image():
#     """
#     Expose the latest image as a read-only MCP resource.
#     """
#     img = scope.get_image()

#     # MCP resources must return JSON-serializable objects
#     # Convert numpy array to nested lists
#     return img.tolist()


#@mcp.resource("latest_image", mime_type="image/png")
@mcp.resource("microscope://latest_image", mime_type="image/png")
def latest_image():
    arr = np.random.randint(0,255,(120,120,3), dtype=np.uint8)
    img = Image.fromarray(arr)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()   # BYTES, NOT STRING


@mcp.prompt()
def tile_scan_xy_with_delay(
    x_positions: list[float],
    y_positions: list[float],
    z: float,
    delay_seconds: float = 1.0,
):
    """
    Runs a 2D tile scan at fixed Z with delay between tiles.
    """

    return f"""
You are controlling a microscope via MCP tools.

Run a tiled XY acquisition:

Fixed Z = {z}
Delay between each tile = {delay_seconds} seconds

X positions: {x_positions}
Y positions: {y_positions}

ACQUISITION LOOP:

FOR each y in Y positions:
  FOR each x in X positions:
    1. Call move_stage(x=x, y=y, z={z})
    2. Call snap_image()
    3. WAIT {delay_seconds} seconds before next tile

Follow this procedure strictly.
Do not skip any tile positions.
Report progress after each tile acquisition.
"""


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
