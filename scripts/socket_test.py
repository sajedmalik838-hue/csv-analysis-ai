import socket
import time

PORT = 8502
HOST = '127.0.0.1'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {HOST}:{PORT}")
        # Keep it open for 30 seconds
        time.sleep(30)
    except Exception as e:
        print(f"Error: {e}")
