import socket
import threading
import struct

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000       # Arbitrary non-privileged port

# Helper to handle each client
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            # First, receive 4 bytes (float) or 4 bytes of 'quit'
            data = conn.recv(4)
            if not data:
                break
            if data == b'quit':
                print(f"Client {addr} requested to quit.")
                break
            # Unpack float (network byte order)
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
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    main() 