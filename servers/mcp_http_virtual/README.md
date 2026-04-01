# microscope_virtual

A virtual microscope MCP server for development and testing of microscope control workflows.

## Overview

This package exposes a simulated microscope as an [MCP](https://modelcontextprotocol.io/) server.
It runs over HTTP (streamable-http transport) so that clients like marimo notebooks can maintain
a persistent connection and share state across multiple tool calls.

## Files

- `microscope_api.py` — the `VirtualMicroscope` class and synthetic test image generators
- `server.py` — FastMCP server wiring tools, resources, and prompts

## Starting the server

```cmd
.venv\Scripts\python.exe microscope_virtual\server.py
```

The server starts on `http://127.0.0.1:4200/mcp` by default.

## MCP Tools

| Tool | Arguments | Description |
|---|---|---|
| `snap_image` | — | Captures an image, saves to a temp file, returns path + metadata |
| `move_stage` | `x, y, z: float` | Moves the stage to absolute (x, y, z) in µm |
| `get_stage_position` | — | Returns current `{x, y, z}` position |
| `wait` | `seconds: float` | Pauses for the given duration |
| `set_test_image` | `source: str` | Switches the virtual image source (see below) |

## MCP Resources

| URI | MIME type | Description |
|---|---|---|
| `microscope://latest_image` | `image/png` | The most recently generated image as raw PNG bytes |

## MCP Prompts

| Prompt | Description |
|---|---|
| `tile_scan_xy` | Generates an LLM prompt to run a 2D tiled XY acquisition at fixed Z |

## Virtual image sources

The `set_test_image` tool accepts one of three sources:

| Source | Description |
|---|---|
| `gradient` | Horizontal grayscale gradient (default, always fast) |
| `rings` | Concentric sine-wave rings — simulates a grayscale fluorescence pattern |
| `spectrum` | RGB color gradient — simulates a multi-channel color image |

All images are generated purely with numpy, no external downloads required.

## Image transfer

Images are **not** sent over the MCP protocol. Instead, `snap_image` saves the PNG to the
system temp directory (`%TEMP%`) and returns the file path in the JSON response. The client
(e.g. marimo) reads the file directly from disk. This avoids binary data going through the
MCP JSON envelope.

## Why HTTP transport?

The server uses `streamable-http` transport instead of stdio so that:

- The server process stays alive between tool calls
- Stage position and other state persist across calls
- Multiple clients can connect simultaneously

## marimo UI (`chat_with_scope.py`)

The companion marimo notebook provides:

- Image source dropdown (`gradient` / `rings` / `spectrum`)
- Step size input (µm)
- XY arrow pad and Z+/Z- buttons for stage control
- Live XYZ position readout
- Snap button with image display
