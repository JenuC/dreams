import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from PIL import Image
    import json
    return Image, json, mo


@app.cell
def _():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    return ClientSession, StdioServerParameters, stdio_client


@app.cell
def _():
    import os
    _base = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.dirname(_base)  # one level up from microscope_mcp/
    PYTHON = os.path.join(_root, ".venv", "Scripts", "python.exe")
    SCRIPT = os.path.join(_base, "server_real.py")
    return PYTHON, SCRIPT


@app.cell
async def _(
    ClientSession,
    PYTHON,
    SCRIPT,
    StdioServerParameters,
    json,
    mo,
    stdio_client,
):
    _params = StdioServerParameters(command=PYTHON, args=[SCRIPT])
    async with stdio_client(_params) as (_r, _w):
        async with ClientSession(_r, _w) as _sess:
            await _sess.initialize()
            _result = await _sess.call_tool("get_stage_position", {})

    _pos = json.loads(_result.content[0].text)
    mo.callout(
        mo.md(f"**Stage** &nbsp; X: `{_pos['x']:.3f}` &nbsp; Y: `{_pos['y']:.3f}` &nbsp; Z: `{_pos['z']:.3f}` µm"),
        kind="info",
    )
    return


@app.cell
async def _(
    ClientSession,
    Image,
    PYTHON,
    SCRIPT,
    StdioServerParameters,
    json,
    mo,
    stdio_client,
):
    _params = StdioServerParameters(command=PYTHON, args=[SCRIPT])
    async with stdio_client(_params) as (_r, _w):
        async with ClientSession(_r, _w) as _sess:
            await _sess.initialize()
            _result = await _sess.call_tool("snap_image", {})

    _data = json.loads(_result.content[0].text)
    print("snap:", _data)
    snap_img = Image.open(_data["image_path"])
    mo.image(snap_img)
    return


if __name__ == "__main__":
    app.run()
