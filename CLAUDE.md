# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**DReAMS** (Data-Reactive Acquisition and Microscope Steering) — a platform for AI-driven smart microscopy. An LLM agent controls a microscope (real or virtual) via MCP tools to implement adaptive, event-driven acquisition workflows.

## Environment setup

Uses `uv` with Python 3.13. Install dependencies:
```
uv sync
```

Activate the venv (Windows):
```
.venv\Scripts\activate
```

## Running the servers

Each server is a standalone Python script run from the repo root:

| Server | Transport | Hardware | Port | Command |
|--------|-----------|----------|------|---------|
| `mcp_http_virtual` | streamable-HTTP | virtual | 4200 | `.venv\Scripts\python.exe servers\mcp_http_virtual\server.py` |
| `mcp_http_real` | streamable-HTTP | real (pycromanager) | 4201 | `.venv\Scripts\python.exe servers\mcp_http_real\server.py` |
| `mcp_stdio_virtual` | stdio | virtual | — | `.venv\Scripts\python.exe servers\mcp_stdio_virtual\server.py` |
| `mcp_stdio_real` | stdio | real (pycromanager) | — | `.venv\Scripts\python.exe servers\mcp_stdio_real\server.py` |
| `openwebui_real` | HTTP/OpenAPI | real (pycromanager) | 4202 | `.venv\Scripts\python.exe servers\openwebui_real\server.py` |

The HTTP servers expose `/mcp` (MCP) or `/tools/*` (Open WebUI).

## Marimo UI notebooks

Each server directory has a companion `marimo_chat.py` notebook. Run from the repo root:
```
.venv\Scripts\marimo.exe run servers\mcp_http_virtual\marimo_chat.py
```
Or in edit mode:
```
.venv\Scripts\marimo.exe edit servers\mcp_http_virtual\marimo_chat.py
```

## Tests

Run all tests:
```
.venv\Scripts\pytest.exe
```

Run a specific test file:
```
.venv\Scripts\pytest.exe servers\openwebui_real\test_openapi.py
```

Smoke-test for real hardware (requires Micro-Manager running with ZMQ server enabled on port 4827):
```
.venv\Scripts\python.exe servers\mcp_stdio_real\test_pycromanager.py
```

## Architecture

### Core library — `dreams/microscope/`

The shared backend lives in `dreams/microscope/`. All servers import from here rather than containing their own hardware logic.

- `common.py` — image utility helpers (`array_to_png_bytes`, `normalise_to_uint8`)
- `virtual.py` — `VirtualMicroscope` and `TestImage` enum; generates numpy test images (gradient, rings, spectrum), no external dependencies
- `real.py` — `RealMicroscope`; wraps `pycromanager.Core` to control real hardware via Micro-Manager's ZMQ bridge
- `__init__.py` — re-exports `RealMicroscope`, `VirtualMicroscope`, `TestImage`

Both `VirtualMicroscope` and `RealMicroscope` implement the same interface: `snap_image()`, `move_stage(x, y, z)`, `get_stage_position()`, `wait(seconds)`, `get_image_png()`.

### Servers — `servers/`

Four MCP servers and one Open WebUI server, organised as `servers/<name>/server.py`. Each server:
1. Walks up the directory tree to locate the repo root and inserts it into `sys.path` so that `dreams.microscope` is importable without installation.
2. Instantiates either `VirtualMicroscope` or `RealMicroscope`.
3. Registers `snap_image`, `move_stage`, `get_stage_position`, `wait` as MCP tools (or FastAPI endpoints for Open WebUI).
4. Exposes `microscope://latest_image` as an MCP resource (PNG bytes).
5. Provides a `tile_scan_xy` MCP prompt for 2D tiled acquisitions.

**Transport choice matters for state:** stdio servers spawn a fresh process per call (stateless). HTTP servers (`mcp_http_*`) keep the process alive across calls, so stage position and image cache persist — required for interactive control from marimo.

### Image transfer convention

`snap_image()` always saves a PNG to the system temp dir and returns the file path in JSON. Images are never sent through the MCP envelope itself; clients (marimo notebooks) read the file directly from disk.

### Open WebUI server (`servers/openwebui_real/`)

Exposes a FastAPI app with a `/tools` manifest endpoint plus individual `POST /tools/<name>` endpoints, conforming to the Open WebUI external tool format. Tests in `test_openapi.py` mock `pycromanager` so they run without hardware.

### Real hardware dependency

`RealMicroscope` requires Micro-Manager 2.0 running with the ZMQ server plugin enabled (default port 4827). `pycromanager` bridges Python to Micro-Manager's Java core. For simulator-based testing, Micro-Manager's `SimCam`/`SimFocus` devices are auto-detected; `RealMicroscope` sets `_focus_device` to `"SimFocus"` when `SimCam` is loaded.
