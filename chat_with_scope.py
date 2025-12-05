import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from PIL import Image
    import io
    import base64
    return Image, base64, io, mo


@app.cell
def _():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    return ClientSession, StdioServerParameters, stdio_client


@app.cell
def _():
    PYTHON = r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python"
    SCRIPT = r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"
    return PYTHON, SCRIPT


@app.cell
async def _(
    ClientSession,
    PYTHON,
    SCRIPT,
    StdioServerParameters,
    stdio_client,
):
    import asyncio

    async def main():
        server_params = StdioServerParameters(
            command=PYTHON,
            args=[SCRIPT],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                print("Available tools:")
                for tool in tools: print(tool)
    await main()
    return asyncio, main


@app.cell
async def _(asyncio, main):
    def run(coro):
        try:
            loop = asyncio.get_running_loop()
            return coro  # marimo/jupyter: let caller await
        except RuntimeError:
            return asyncio.run(coro)  

    result = run(main())
    if asyncio.iscoroutine(result):
        result = await result
    return


@app.cell
async def _(ClientSession, StdioServerParameters, base64, io, stdio_client):
    async def fetch_latest_imagexx():
        server_params = StdioServerParameters(
            command=r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python.exe",
            args=[r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                resources = (await session.list_resources()).resources
                uri = str(resources[0].uri)

                raw = await session.read_resource(uri)
                content = raw.contents[0]

                # ----- robust MCP payload extraction -----

                if hasattr(content, "data"):           # BinaryResourceContents
                    payload = content.data

                elif hasattr(content, "blob"):         # BlobResourceContents
                    blob = content.blob
                    payload = base64.b64decode(blob) if isinstance(blob, str) else blob

                elif hasattr(content, "text"):         # TextResourceContents
                    print("TEXT RESOURCE:")
                    print(content.text)
                    return None

                else:
                    raise TypeError(f"Unhandled MCP resource type: {type(content)}")

                # payload is now guaranteed bytes
                print(len(payload))
                img = io.BytesIO(payload)
                return img


    # ---- run in marimo ----
    result3 = await fetch_latest_imagexx()

    return (result3,)


@app.cell
def _(Image, result3):
    imgx = Image.open(result3)
    imgx
    return


@app.cell
def _():
    return


@app.cell
def _():
    import numpy as np
    volume = np.random.rand(30, 200, 200)
    return (volume,)


@app.cell
def _(mo, volume):
    def _(volume):
        z_slider = mo.ui.slider(
            start=0,
            stop=volume.shape[0] - 1,
            step=1,
            label="Z slice"
        )

        tabs = mo.ui.tabs(
            {
                "Slide 1 — Overview": mo.md(
                    """
                    ## 3D Volume Viewer Demo

                    - This app shows a random 3D numpy array.
                    - Use the Z slider to change slices.
                    - The image updates in real time.
                    """
                ),
                "Slide 2 — Controls": mo.vstack(
                    [
                        mo.md("### Z Navigation"),
                        z_slider,
                    ]
                ),
                "Slide 3 — Image Viewer": mo.vstack(
                    [
                        mo.md("### Current Slice"),
                        z_slider,   # repeat slider for convenience
                    ]
                ),
            }
        )

        return tabs, z_slider

    tabs,zslider = _(volume=volume)

    return (zslider,)


@app.cell
def _(zslider):
    zslider
    return


@app.cell
def _(mo, volume, zslider):
    def _(volume, z_slider):
        z = int(z_slider.value)
        slice_img = volume[z]

        viewer = mo.image(
            src=slice_img,
            width=450,
            caption=f"Z = {z}"
        )

        mo.vstack(
            [
                mo.md("## Live Slice Viewer"),
                viewer,
            ]
        )

        return viewer

    _(volume=volume,z_slider=zslider)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
