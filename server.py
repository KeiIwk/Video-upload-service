import socket
import os
import threading
import config

storage_used = 0
lock = threading.Lock()

def handle_client(client_socket, address):
    global storage_used

    try:
        print(f"[{address}] connection accepted。")

        file_size_data = client_socket.recv(32)
        file_size = int.from_bytes(file_size_data, byteorder='big')
        
        if file_size + storage_used > config.MAX_STORAGE:
            client_socket.sendall(b"STORAGE_LIMIT_REACHED".ljust(16))
            print(f"[{address}] reached size limit")
            client_socket.close()
            return

        file_path = f"received_{address[0]}_{address[1]}.mp4"
        with open(file_path, 'wb') as f:
            received_size = 0

            while received_size < file_size:
                data = client_socket.recv(config.PACKET_SIZE)
                if not data:
                    break

                f.write(data)
                received_size += len(data)

        if received_size == file_size:
            with lock:
                storage_used += file_size

            client_socket.sendall(b"UPLOAD_SUCCESS".ljust(16))
            print(f"[{address}] file uploaded successfully: {file_path}")
        else:
            os.remove(file_path)
            client_socket.sendall(b"UPLOAD_FAILED".ljust(16))
            print(f"[{address}] file upload failed.")

    except Exception as e:
        print(f"[{address}] error occured: {e}")
        client_socket.sendall(b"UPLOAD_FAILED".ljust(16))

    finally:
        client_socket.close()
        print(f"[{address}] closed.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((config.HOST, config.PORT))
    server.listen(5)
    print(f"server started. PORT: {config.PORT}")

    while True:
        client_socket, address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
