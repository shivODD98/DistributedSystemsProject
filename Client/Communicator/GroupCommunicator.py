import socket
import time
class GroupCommunicator:

    def __init__(self):
        # self.server_ip = server_ip
        # self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initalize(self, queueLength = 10):
        # Start a socket server to listen on a free port that is to be determined
        self.socket.bind((socket.gethostname(), 0))

        return self.socket.getsockname()


    # TODO: need to make this on a new thread because it completly hangs the console
    def start(self):

        print("UDP server is starting...")
        time.sleep(2)
        print("UDP server is ending...")
        # while True:
        #     data,addr = self.socket.recvfrom(1024)
        #     print(f"received message: {data} from: {addr}")

