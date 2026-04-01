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
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    MCP_URL = "http://127.0.0.1:4201/mcp"
    return ClientSession, MCP_URL, streamablehttp_client


@app.cell
def _(mo):
    step_size = mo.ui.number(value=10.0, start=0.1, stop=10000.0, step=1.0, label="Step (µm)")
    btn_snap = mo.ui.button(label="📷 Snap")
    btn_xp   = mo.ui.button(label="➡ X+")
    btn_xm   = mo.ui.button(label="⬅ X-")
    btn_yp   = mo.ui.button(label="⬆ Y+")
    btn_ym   = mo.ui.button(label="⬇ Y-")
    btn_zp   = mo.ui.button(label="🔼 Z+")
    btn_zm   = mo.ui.button(label="🔽 Z-")

    mo.vstack([
        mo.hstack([step_size, btn_snap], justify="start"),
        mo.hstack([
            mo.vstack([
                mo.md("**XY**"),
                mo.hstack([btn_yp], justify="center"),
                mo.hstack([btn_xm, btn_xp], justify="center"),
                mo.hstack([btn_ym], justify="center"),
            ]),
            mo.vstack([
                mo.md("**Z**"),
                btn_zp,
                btn_zm,
            ]),
        ], justify="start", gap=4),
    ])
    return btn_snap, btn_xm, btn_xp, btn_ym, btn_yp, btn_zm, btn_zp, step_size


@app.cell
async def _(
    ClientSession,
    MCP_URL,
    btn_xp,
    json,
    step_size,
    streamablehttp_client,
):
    _trigger = btn_xp.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _cur = json.loads((await _s.call_tool("get_stage_position", {})).content[0].text)
            _res = await _s.call_tool("move_stage", {"x": _cur["x"] + step_size.value, "y": _cur["y"], "z": _cur["z"]})
    pos_xp = json.loads(_res.content[0].text)
    return (pos_xp,)


@app.cell
async def _(
    ClientSession,
    MCP_URL,
    btn_xm,
    json,
    step_size,
    streamablehttp_client,
):
    _trigger = btn_xm.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _cur = json.loads((await _s.call_tool("get_stage_position", {})).content[0].text)
            _res = await _s.call_tool("move_stage", {"x": _cur["x"] - step_size.value, "y": _cur["y"], "z": _cur["z"]})
    pos_xm = json.loads(_res.content[0].text)
    return (pos_xm,)


@app.cell
async def _(
    ClientSession,
    MCP_URL,
    btn_yp,
    json,
    step_size,
    streamablehttp_client,
):
    _trigger = btn_yp.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _cur = json.loads((await _s.call_tool("get_stage_position", {})).content[0].text)
            _res = await _s.call_tool("move_stage", {"x": _cur["x"], "y": _cur["y"] + step_size.value, "z": _cur["z"]})
    pos_yp = json.loads(_res.content[0].text)
    return (pos_yp,)


@app.cell
async def _(
    ClientSession,
    MCP_URL,
    btn_ym,
    json,
    step_size,
    streamablehttp_client,
):
    _trigger = btn_ym.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _cur = json.loads((await _s.call_tool("get_stage_position", {})).content[0].text)
            _res = await _s.call_tool("move_stage", {"x": _cur["x"], "y": _cur["y"] - step_size.value, "z": _cur["z"]})
    pos_ym = json.loads(_res.content[0].text)
    return (pos_ym,)


@app.cell
async def _(
    ClientSession,
    MCP_URL,
    btn_zp,
    json,
    step_size,
    streamablehttp_client,
):
    _trigger = btn_zp.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _cur = json.loads((await _s.call_tool("get_stage_position", {})).content[0].text)
            _res = await _s.call_tool("move_stage", {"x": _cur["x"], "y": _cur["y"], "z": _cur["z"] + step_size.value})
    pos_zp = json.loads(_res.content[0].text)
    return (pos_zp,)


@app.cell
async def _(
    ClientSession,
    MCP_URL,
    btn_zm,
    json,
    step_size,
    streamablehttp_client,
):
    _trigger = btn_zm.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _cur = json.loads((await _s.call_tool("get_stage_position", {})).content[0].text)
            _res = await _s.call_tool("move_stage", {"x": _cur["x"], "y": _cur["y"], "z": _cur["z"] - step_size.value})
    pos_zm = json.loads(_res.content[0].text)
    return (pos_zm,)


@app.cell
def _(mo, pos_xm, pos_xp, pos_ym, pos_yp, pos_zm, pos_zp):
    _candidates = [p for p in [pos_xp, pos_xm, pos_yp, pos_ym, pos_zp, pos_zm] if p is not None]
    _pos = _candidates[-1] if _candidates else {"x": 0.0, "y": 0.0, "z": 0.0}
    mo.callout(
        mo.md(f"**Stage** &nbsp; X: `{_pos['x']:.3f}` &nbsp; Y: `{_pos['y']:.3f}` &nbsp; Z: `{_pos['z']:.3f}` µm"),
        kind="info",
    )
    return


@app.cell
async def _(
    ClientSession,
    Image,
    MCP_URL,
    btn_snap,
    json,
    mo,
    streamablehttp_client,
):
    _trigger = btn_snap.value
    async with streamablehttp_client(MCP_URL) as (_r, _w, _):
        async with ClientSession(_r, _w) as _s:
            await _s.initialize()
            _result = await _s.call_tool("snap_image", {})

    _data = json.loads(_result.content[0].text)
    print("snap:", _data)
    snap_img = Image.open(_data["image_path"])
    mo.image(snap_img)
    return


if __name__ == "__main__":
    app.run()
