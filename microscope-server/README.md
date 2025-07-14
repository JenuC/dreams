# Microscope MCP Server

This project implements a Model Context Protocol (MCP) server for controlling a simulated microscope.

## Features

- Snap an image from the camera (`snap_image`).
- Move the stage in the XY plane (`move_xy`).
- Adjust the focus (Z-axis) (`move_z`).

## Installation

-   On Windows:
    ```bash
    uv venv
    .venv\Scripts\activate
    uv pip install -r requirements.txt
    ```

## Running the Server

To run the MCP server, execute the following command from the `microscope-server` directory:
```bash
python server.py
```

## Running the Test Client

A test client is provided to demonstrate how to interact with the server's tools.
Run the test client:
    ```bash
    python test_client.py
    ```

## MCP Configuration
To use this server with an MCP-compatible client, you will need to configure it in your client's settings. Here is an example configuration:

```json
{
  "mcpServers": {
    "microscope": {
      "command": "python",
      "args": [
        "path/to/your/project/microscope-server/server.py"
      ],
      "cwd": "path/to/your/project/microscope-server",
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
```

Replace `path/to/your/project` with the absolute path to the project directory. The `command` should be the python executable within the virtual environment if you want to be specific, or just `python` if the virtual environment is activated in the context where the MCP client is launched.