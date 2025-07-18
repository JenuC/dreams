from mcp.server.fastmcp import FastMCP
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

mcp = FastMCP(name="microscope-server", version="0.1.0")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Return the sum of two numbers."""
    return a + b

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle."""
    print("Microscope server starting up...")
    yield
    print("Microscope server shutting down...")

app = FastAPI(lifespan=lifespan)

# Add FastAPI endpoints that call your MCP tools
@app.post("/mcp/add")
async def add_endpoint(data: dict):
    a = data.get("a")
    b = data.get("b")
    return {"result": add(a, b)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)