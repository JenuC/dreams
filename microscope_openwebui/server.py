from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from microscope_api import RealMicroscope

app = FastAPI(title="Microscope Open WebUI Tool Server")

scope = RealMicroscope()


# ---------------------------------------------------------------------------
# Pydantic models for the Open WebUI tool manifest
# ---------------------------------------------------------------------------

class ToolParameter(BaseModel):
    type: str
    properties: dict
    required: list[str]


class ToolEntry(BaseModel):
    name: str
    description: str
    parameters: ToolParameter


class ToolManifest(BaseModel):
    tools: list[ToolEntry]


# ---------------------------------------------------------------------------
# Tool manifest
# ---------------------------------------------------------------------------

_MANIFEST = ToolManifest(
    tools=[
        ToolEntry(
            name="snap_image",
            description="Capture an image from the microscope at the current stage position.",
            parameters=ToolParameter(
                type="object",
                properties={},
                required=[],
            ),
        ),
        ToolEntry(
            name="move_stage",
            description="Move the microscope stage to the given (x, y, z) coordinates in µm.",
            parameters=ToolParameter(
                type="object",
                properties={
                    "x": {"type": "number", "description": "X coordinate in µm"},
                    "y": {"type": "number", "description": "Y coordinate in µm"},
                    "z": {"type": "number", "description": "Z coordinate in µm"},
                },
                required=["x", "y", "z"],
            ),
        ),
        ToolEntry(
            name="get_stage_position",
            description="Return the current stage position as {x, y, z}.",
            parameters=ToolParameter(
                type="object",
                properties={},
                required=[],
            ),
        ),
        ToolEntry(
            name="wait",
            description="Pause execution for the given number of seconds.",
            parameters=ToolParameter(
                type="object",
                properties={
                    "seconds": {"type": "number", "description": "Duration to wait in seconds"},
                },
                required=["seconds"],
            ),
        ),
    ]
)


@app.get("/tools")
def get_tools() -> dict:
    """Return the Open WebUI tool manifest listing all available microscope tools."""
    return _MANIFEST.model_dump()


# ---------------------------------------------------------------------------
# Request models for tool endpoints
# ---------------------------------------------------------------------------

class MoveStageRequest(BaseModel):
    x: float
    y: float
    z: float


class WaitRequest(BaseModel):
    seconds: float


# ---------------------------------------------------------------------------
# Tool endpoints
# ---------------------------------------------------------------------------

@app.post("/tools/snap_image")
def snap_image():
    try:
        return scope.snap_image()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/tools/move_stage")
def move_stage(req: MoveStageRequest):
    try:
        return scope.move_stage(req.x, req.y, req.z)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/tools/get_stage_position")
def get_stage_position():
    try:
        return scope.get_stage_position()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/tools/wait")
def wait(req: WaitRequest):
    try:
        return scope.wait(req.seconds)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


# ---------------------------------------------------------------------------
# Entry point (added in task 9)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4202)
