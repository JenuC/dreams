import socket
import struct

HOST = '127.0.0.1'  # Server address (localhost by default)
PORT = 5000         # Must match server


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")
        while True:
            user_input = input("Enter a float value to send, 'quit' to exit, or 'close' to shutdown server: ")
            if user_input.strip().lower() == 'quit':
                s.sendall(b'quit')
                print("Disconnected from server.")
                break
            if user_input.strip().lower() == 'close':
                s.sendall(b'clos')
                print("Sent server shutdown command. Disconnected.")
                break
            try:
                value = float(user_input)
                packed = struct.pack('!f', value)
                s.sendall(packed)
            except ValueError:
                print("Invalid input. Please enter a valid float, 'quit', or 'close'.")

if __name__ == "__main__":
    main() 