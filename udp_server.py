import socket
import os
import hashlib  # needed to verify file hash

IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_info(data: bytes) -> (str, int):
    return data[8:].decode(), int.from_bytes(data[:8], byteorder='big')


def upload_file(server_socket: socket, file_name: str, file_size: int):
    # create a SHA256 object to verify file hash
    # TODO: section 1 step 5 in README.md file
    obj = hashlib.sha256()

    # create a new file to store the received data
    with open(file_name + '.temp', 'wb') as file:
        # TODO: section 1 step 7a - 7e in README.md file
        bytes_received = 0
        while bytes_received < file_size:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            file.write(data)
            bytes_received += data
            obj.update(data)

            server_socket.sendto(b'received', client_address)
    # get hash from client to verify
    client_hash,client_address = server_socket.recv(BUFFER_SIZE)
    client_hash = client_hash.decode()
    server_hash = obj.hexdigest()

    # TODO: section 1 step 8 in README.md file
    if client_hash == server_hash:
        os. rename(file_name+'.temp', file_name)
        server_socket.sendto(b'success',client_address)
        print(f'{file_name} success')
    else:
        os.remove(file_name+'.temp')
        server_socket.sendto(b'failed',client_address)
        print(f'{file_name}failed')


    # TODO: section 1 step 9 in README.md file


def start_server():
    # create a UDP socket and bind it to the specified IP and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f'Server ready and listening on {IP}:{PORT}')


    try:
        while True:
            # TODO: section 1 step 2 in README.md file
            # expecting an 8-byte byte string for file size followed by file name
            data, client_address = server_socket.recvfrom(1024)
            file_name, file_size = get_file_info(data)

            server_socket.sendto(b'go ahead', client_address)
            upload_file(server_socket, file_name, file_size)

            # TODO: section 1 step 3 in README.md file
            # TODO: section 1 step 4 in README.md file
            upload_file(server_socket, file_name, file_size)
    except KeyboardInterrupt as ki:
        pass
    except Exception as e:
        print(f'An error occurred while receiving the file:str {e}')
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()
