import config
import socket
import os


def send_file(file_path):
    if not os.path.exists(file_path):
        print("Error: file {} not found".format(file_path))
        return
    
    file_size = os.path.getsize(file_path)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((config.SERVER_HOST, config.SERVER_PORT))
            print("Server {}:{} connection established.".format(config.SERVER_HOST, config.SERVER_PORT))

            client_socket.sendall(file_size.to_bytes(32, byteorder='big'))

            with open(file_path, 'rb') as f:
                while (chunk := f.read(config.PACKET_SIZE)):
                    client_socket.sendall(chunk)

            response = client_socket.recv(16).strip()
            print("Server: {}".format(response.decode('utf-8')))

        except Exception as e:
            print("Error occured: {}".format(e))

if __name__ == "__main__":
    file_path = input("Input MP4 file's path: ").strip()
    if file_path.endswith(".mp4"):
        send_file(file_path)
    else:
        print("Error: only MP4 can be uploaded.")


