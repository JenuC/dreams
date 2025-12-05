import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


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
                print("Available tools:", tools)

                # Example: call the add tool
                #result = await session.call_tool("add", {"a": 4, "b": 5})
                #print("add(4,5) =", result)

    #asyncio.run(main())

    await main()
    return asyncio, main


@app.cell
async def _(asyncio, main):
    def run(coro):
        try:
            loop = asyncio.get_running_loop()
            return coro  # marimo/jupyter: let caller await
        except RuntimeError:
            return asyncio.run(coro)  # plain python

    result = run(main())

    # If running in marimo:
    if asyncio.iscoroutine(result):
        result = await result
    return


@app.cell
def _(mo):
    mo.md(r"""
    from PIL import Image
    import io

    async def fetch_and_display():

        server_params = StdioServerParameters(
            command=r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python.exe",
            args=[r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                resource = await session.read_resource("latest_image")

                # Extract bytes
                blob = resource.contents[0].data
                img = Image.open(io.BytesIO(blob))

                return img

    img1 = await fetch_and_display()
    img1
    """)
    return


@app.cell
def _(ClientSession, StdioServerParameters, stdio_client):
    async def get_resource():

        server_params = StdioServerParameters(
            command=r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python.exe",
            args=[r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # ---- FETCH RESOURCE ----
                #resource = await session.read_resource("latest_image")
                #resource = await session.read_resource("microscope://latest_image")
                #return resource
                #res = await session.list_resources()
                #return res.resources

                resources = (await session.list_resources()).resources
                uri = str(resources[0].uri)

                resource = await session.read_resource(uri)
                return resource
    return (get_resource,)


@app.cell
def _(get_resource):
    raw_resource = get_resource()
    #raw_resource
    return


@app.cell
def _():
    from PIL import Image
    import io
    return Image, io


@app.cell
def _():
    # MCP resources return 1+ content items
    #content = raw_resource.contents[0]

    # Get raw bytes
    #image_bytes = content.data

    # Load with PIL
    #mg = Image.open(io.BytesIO(content.text))
    #type(content)
    #content.text



    return


@app.cell
def _(mo):
    mo.md(r"""
    async def fetch_latest_image():

        server_params = StdioServerParameters(
            # Use the SAME python interpreter that has MCP installed
            command=r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python.exe",
            args=[r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # MCP handshake
                await session.initialize()

                # ----------------------------
                # DISCOVER SERVER FEATURES
                # ----------------------------

                tools = (await session.list_tools()).tools
                print("TOOLS:")
                for t in tools:
                    print(f"  - {t.name}: {t.description}")

                resources = (await session.list_resources()).resources
                print("\nRESOURCES:")
                for r in resources:
                    print(f"  - {r.name} -> {r.uri} ({r.mimeType})")

                # ----------------------------
                # LOAD FIRST IMAGE RESOURCE
                # ----------------------------

                if not resources:
                    raise RuntimeError("No MCP resources published by server")

                uri = str(resources[0].uri)
                print("\nFETCHING RESOURCE:", uri)

                raw = await session.read_resource(uri)
                content = raw.contents[0]

                # ----------------------------
                # HANDLE BINARY vs TEXT
                # ----------------------------

                if hasattr(content, "data"):
                    # Binary resource (image/png, etc)
                    img_bytes = content.data
                    img = Image.open(io.BytesIO(img_bytes))
                    return img

                elif hasattr(content, "text"):
                    # Text resource
                    print("\nTEXT RESOURCE OUTPUT:\n")
                    print(content.text)
                    return None

                else:
                    raise TypeError(f"Unknown resource content type: {type(content)}")
    """)
    return


@app.cell
def _(ClientSession, Image, StdioServerParameters, io, stdio_client):
    async def fetch_latest_imagex():

        server_params = StdioServerParameters(
            command=r"C:\Users\lociuser\code\jenu\dreams\.venv\Scripts\python.exe",
            args=[r"C:\Users\lociuser\code\jenu\dreams\microscope_mcp\server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Show advertised resources for sanity
                resources = (await session.list_resources()).resources
                print("RESOURCES:", resources)

                if not resources:
                    raise RuntimeError("No MCP resources available")

                uri = str(resources[0].uri)
                raw = await session.read_resource(uri)

                content = raw.contents[0]

                # ---- Handle all valid MCP content types ----
                if hasattr(content, "data"):
                    payload = content.data        # BinaryResourceContents

                elif hasattr(content, "blob"):
                    payload = content.blob        # ✅ BlobResourceContents

                elif hasattr(content, "text"):
                    print("TEXT RESOURCE:")
                    print(content.text)
                    return None

                else:
                    raise TypeError(f"Unhandled MCP resource type: {type(content)}")

                # Decode PNG into PIL image
                img = Image.open(io.BytesIO(payload))
                return img
    return


@app.cell
def _():
    #result1 = await fetch_latest_imagex()

    # Display image or fallback notice
    #result1 if result1 is not None else "No binary image returned"
    return


@app.cell
def _():
    import base64
    return (base64,)


@app.cell
async def _(
    ClientSession,
    Image,
    StdioServerParameters,
    base64,
    io,
    stdio_client,
):


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
                img = Image.open(io.BytesIO(payload))
                return img


    # ---- run in marimo ----
    result3 = await fetch_latest_imagexx()
    result3

    return


@app.cell
def _():
    return


@app.cell
def _():
    #blob = raw_resource.contents[0].data
    return


@app.cell
def _():
    #img
    return


@app.cell
def _():
    return


@app.cell
def _():
    #git status
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
