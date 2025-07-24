import socket
import struct

HOST = '127.0.0.1'  # Server address (localhost by default)
PORT = 5000         # Must match server


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")
        while True:
            user_input = input("Enter a float value to send (or 'quit' to exit): ")
            if user_input.strip().lower() == 'quit':
                s.sendall(b'quit')
                print("Disconnected from server.")
                break
            try:
                value = float(user_input)
                packed = struct.pack('!f', value)
                s.sendall(packed)
            except ValueError:
                print("Invalid input. Please enter a valid float or 'quit'.")

if __name__ == "__main__":
    main() 