import socket

class GroupCommunicator:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socker(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.socket.bind((self.server_ip, self.server_port))

        while True:
            data,addr = sock.recvfrom(1024)
            print(f"received message: {data} from: {addr}")

