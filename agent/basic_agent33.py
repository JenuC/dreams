import requests
import json


def debug_mcp():
    url = "http://127.0.0.1:8000/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    # 1. Initialize
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

    print("Sending initialize message...")
    response = requests.post(url, json=init_msg, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Raw Response: '{response.text}'")
    print(f"Response Length: {len(response.text)}")

    # Only try to parse JSON if we got a 200 response and non-empty content
    if response.status_code == 200 and response.text.strip():
        try:
            json_response = response.json()
            print("JSON Response:", json.dumps(json_response, indent=2))
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response content: {repr(response.text)}")
    else:
        print("Not attempting JSON parse due to status code or empty response")

    # Try a simple GET request to see if the server is responding at all
    print("\n" + "=" * 50)
    print("Testing GET request to base URL...")

    try:
        get_response = requests.get("http://127.0.0.1:8000/mcp")
        print(f"GET Status Code: {get_response.status_code}")
        print(f"GET Response: '{get_response.text}'")
    except Exception as e:
        print(f"GET Error: {e}")

    # Try without custom headers
    print("\n" + "=" * 50)
    print("Testing POST without custom headers...")

    try:
        simple_response = requests.post(url, json=init_msg)
        print(f"Simple POST Status Code: {simple_response.status_code}")
        print(f"Simple POST Response: '{simple_response.text}'")
    except Exception as e:
        print(f"Simple POST Error: {e}")


if __name__ == "__main__":
    debug_mcp()
