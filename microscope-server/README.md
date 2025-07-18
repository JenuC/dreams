# Microscope MCP Server

This project implements a Model Context Protocol (MCP) server for controlling a simulated microscope.

## Features

- Snap an image from the camera (`snap_image`).
- Move the stage in the XY plane (`move_xy`).
- Adjust the focus (Z-axis) (`move_z`).

## Installation

This project uses `uv` for package and environment management.

1.  **Create a virtual environment:**
    ```bash
    uv venv
    ```

2.  **Activate the virtual environment:**
    -   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

## Running the Server

To run the MCP server, execute the following command from the `microscope-server` directory:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```

## MCP Configuration

This server runs as a remote SSE server. To use this server with an MCP-compatible client, you will need to configure it in your client's settings. Here is an example configuration:

```json
{
  "mcpServers": {
    "microscope": {
      "url": "http://127.0.0.1:8000",
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}