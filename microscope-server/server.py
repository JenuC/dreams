import socket
import threading
import struct
import sys

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000       # Arbitrary non-privileged port

shutdown_event = threading.Event()

# Helper to handle each client
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while not shutdown_event.is_set():
            data = conn.recv(4)
            if not data:
                break
            if data == b'quit':
                print(f"Client {addr} requested to quit.")
                break
            if data == b'clos':
                print(f"Client {addr} requested server shutdown.")
                shutdown_event.set()
                break
            if data == b'gtsg':
                print(f"Client {addr} requested stage location. Sending 300.0, 499.9.")
                response = struct.pack('!ff', 300.0, 499.9)
                conn.sendall(response)
                continue
            if data == b'move':
                coords = conn.recv(8)
                if len(coords) == 8:
                    x, y = struct.unpack('!ff', coords)
                    print(f"Client {addr} requested move to: x={x}, y={y}")
                else:
                    print(f"Client {addr} sent incomplete move coordinates: {coords}")
                continue
            try:
                value = struct.unpack('!f', data)[0]
                print(f"Received from {addr}: {value}")
            except struct.error:
                print(f"Malformed data from {addr}: {data}")
    finally:
        conn.close()
        print(f"Connection closed for {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        threads = []
        while not shutdown_event.is_set():
            try:
                s.settimeout(1.0)
                conn, addr = s.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
                threads.append(thread)
            except socket.timeout:
                continue
            except OSError:
                break
        print("Server shutting down. Waiting for client threads to finish...")
        shutdown_event.set()
        for t in threads:
            t.join()
        print("Server has shut down.")

if __name__ == "__main__":
    main() 