import requests
import json
import re


def parse_sse_response(response_text):
    """Parse Server-Sent Events format to extract JSON data"""
    # Look for data: lines in the SSE response
    data_pattern = r"data: (.+)"
    matches = re.findall(data_pattern, response_text)

    if matches:
        # Return the JSON data from the first data: line
        return json.loads(matches[0])
    return None


def send_mcp_message(url, message, headers):
    """Send MCP message and parse SSE response"""
    response = requests.post(url, json=message, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")

    # Check for session ID in response headers
    session_id = response.headers.get("mcp-session-id")
    if session_id:
        print(f"Session ID: {session_id}")

    if response.status_code == 200:
        if "text/event-stream" in response.headers.get("content-type", ""):
            # Parse SSE format
            json_data = parse_sse_response(response.text)
            if json_data:
                print("Parsed JSON:", json.dumps(json_data, indent=2))
                return json_data, session_id
            else:
                print("No JSON data found in SSE response")
                print("Raw response:", repr(response.text))
        else:
            # Regular JSON response
            return response.json(), session_id
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")

    return None, None


def test_mcp_working():
    url = "http://127.0.0.1:8000/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    print("=== INITIALIZE ===")
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"},
        },
    }

    init_result, session_id = send_mcp_message(url, init_msg, headers)

    if init_result and init_result.get("result") and session_id:
        print("✓ Initialize successful")

        headers_with_session = headers.copy()
        headers_with_session["mcp-session-id"] = session_id

        print("\n=== LIST TOOLS ===")
        list_msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

        tools_result, _ = send_mcp_message(url, list_msg, headers_with_session)

        if tools_result and tools_result.get("result"):
            print("✓ Tools list successful")
            tools = tools_result["result"].get("tools", [])
            print(f"Available tools: {[tool['name'] for tool in tools]}")

            print("\n=== CALL ADD TOOL ===")
            call_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "add", "arguments": {"a": 5, "b": 3}},
            }

            call_result, _ = send_mcp_message(url, call_msg, headers_with_session)

            if call_result and call_result.get("result"):
                print("✓ Tool call successful")
                print("Result:", call_result["result"])
            else:
                print("✗ Tool call failed")
        else:
            print("✗ Tools list failed")
    else:
        print("✗ Initialize failed - no session ID received")


if __name__ == "__main__":
    test_mcp_working()
