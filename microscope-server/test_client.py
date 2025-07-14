import asyncio
import json

# This is a mock client to simulate sending requests to the MCP server.
# In a real scenario, an MCP client would handle the communication.

async def send_request(tool_name, params=None):
    """Simulates sending a request to the MCP server."""
    request = {
        "tool_name": tool_name,
        "params": params or {}
    }
    print(f"-> Sending request: {json.dumps(request, indent=2)}")
    # In a real client, this would involve sending the request over a transport (e.g., stdio)
    # and waiting for a response. For this test, we'll just print the request.
    print("<- Received simulated response (see server output for actual execution)")


async def main():
    print("--- Microscope Test Client ---")

    # Test case 1: Snap an image
    await send_request("snap_image")
    await asyncio.sleep(1)

    # Test case 2: Move the stage
    await send_request("move_xy", {"x": 10.5, "y": -5.2})
    await asyncio.sleep(1)

    # Test case 3: Adjust the focus
    await send_request("move_z", {"z": 2.0})

    print("\n--- Test complete ---")

if __name__ == "__main__":
    asyncio.run(main())