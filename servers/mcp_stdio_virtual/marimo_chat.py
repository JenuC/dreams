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
    PYTHON = r"C:\Users\jenuv\code\dreams\.venv\Scripts\python.exe"
    SCRIPT = r"C:\Users\jenuv\code\dreams\microscope_mcp\server.py"
    return PYTHON, SCRIPT


# ── image source selector ─────────────────────────────────────────────────────

@app.cell
def _(mo):
    source_picker = mo.ui.dropdown(
        options=["gradient", "camera", "raccoon"],
        value="gradient",
        label="Test image source",
    )
    source_picker
    return (source_picker,)


# ── snap image (source from dropdown, single connection) ──────────────────────

@app.cell
async def _(ClientSession, Image, PYTHON, SCRIPT, StdioServerParameters, json, mo, source_picker, stdio_client):
    _params = StdioServerParameters(command=PYTHON, args=[SCRIPT])
    async with stdio_client(_params) as (_r2, _w2):
        async with ClientSession(_r2, _w2) as _sess2:
            await _sess2.initialize()
            await _sess2.call_tool("set_test_image", {"source": source_picker.value})
            _result = await _sess2.call_tool("snap_image", {})

    _data = json.loads(_result.content[0].text)
    print("snap:", _data)
    snap_img = Image.open(_data["image_path"])
    mo.image(snap_img)
    return (snap_img,)


if __name__ == "__main__":
    app.run()
