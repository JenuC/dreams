import requests

MCP_BASE = "http://localhost:8000/mcp"


def move_stage(x, y):
    resp = requests.post(f"{MCP_BASE}/move_xy", json={"x": x, "y": y})
    print("Move Stage Response:", resp.json())


def snap_image():
    resp = requests.post(f"{MCP_BASE}/snap_image")
    print("Snap Image Response:", resp.json())


def agent_loop():
    print("Type a command: (move x y | snap | quit)")
    while True:
        cmd = input("> ").strip()
        if cmd == "quit":
            break
        elif cmd.startswith("move"):
            _, x, y = cmd.split()
            move_stage(float(x), float(y))
        elif cmd == "snap":
            snap_image()
        else:
            print("Unknown command")


if __name__ == "__main__":
    agent_loop()
