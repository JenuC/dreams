# mcp_http_virtual

A virtual microscope MCP server for development and testing of microscope control workflows.

## Overview

This package exposes a simulated microscope as an [MCP](https://modelcontextprotocol.io/) server.
It runs over HTTP (streamable-http transport) so that clients like marimo notebooks can maintain
a persistent connection and share state across multiple tool calls.

## Files

- `server.py` — FastMCP streamable-HTTP server wiring
- `marimo_chat.py` — companion marimo UI for stage control and image capture
- `dreams/microscope/virtual.py` — shared `VirtualMicroscope` backend

## Starting the server

```cmd
.venv\Scripts\python.exe servers\mcp_http_virtual\server.py
```

The server starts on `http://127.0.0.1:4200/mcp` by default.

## MCP Tools

- `snap_image`: captures an image, saves it to a temp file, and returns path + metadata.
- `move_stage(x, y, z)`: moves the stage to absolute coordinates in µm.
- `get_stage_position()`: returns the current `{x, y, z}` position.
- `wait(seconds)`: pauses for the given duration.
- `set_test_image(source)`: switches the virtual image source.

## MCP Resources

- `microscope://latest_image` (`image/png`): the latest generated image as raw PNG bytes.

## MCP Prompts

- `tile_scan_xy`: generates an LLM prompt to run a 2D tiled XY acquisition at fixed Z.

## Virtual image sources

The `set_test_image` tool accepts one of three sources:

- `gradient`: horizontal grayscale gradient.
- `rings`: concentric sine-wave rings that simulate a fluorescence-like pattern.
- `spectrum`: RGB color gradient that simulates a multi-channel image.

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

## marimo UI (`marimo_chat.py`)

The companion marimo notebook provides:

- Image source dropdown (`gradient` / `rings` / `spectrum`)
- Step size input (µm)
- XY arrow pad and Z+/Z- buttons for stage control
- Live XYZ position readout
- Snap button with image display
