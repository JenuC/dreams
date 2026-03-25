import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from PIL import Image
    import io
    import base64
    return Image, base64, io


@app.cell
def _():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    return ClientSession, StdioServerParameters, stdio_client


@app.cell
def _():
    ## SLIM

    PYTHON = r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python"
    SCRIPT = r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"

    ## KRAKEN

    PYTHON = r"C:\Users\jenuv\code\dreams\.venv\Scripts\python.exe"
    SCRIPT = r"C:\Users\jenuv\code\dreams\microscope_mcp\server.py"

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
async def _(
    ClientSession,
    PYTHON,
    SCRIPT,
    StdioServerParameters,
    base64,
    io,
    stdio_client,
):
    async def fetch_latest_imagexx():
        server_params = StdioServerParameters(
            command=PYTHON,
            args=[SCRIPT],
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
    return


if __name__ == "__main__":
    app.run()
