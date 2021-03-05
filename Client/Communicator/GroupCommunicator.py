import re
import socket
import time
from Communicator.SnipManagementThread import SnipManagementThread
from Communicator.PeerManagementThread import PeerManagementThread
from Communicator.SnipManager import SnipManager

class GroupCommunicator:

    def __init__(self, group_manager, snipManager):
        # self.server_ip = server_ip
        # self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.group_manager = group_manager
        self.snipManager = snipManager
        self.isAlive = 1
        self.threads = []

    def initalize(self, queueLength = 10):
        # Start a socket server to listen on a free port that is to be determined
        self.socket.bind((socket.gethostname(), 0))

        return self.socket.getsockname()

    # TODO: need to make this on a new thread because it completly hangs the console
    def start(self):

        print("UDP server is starting...")
        peerManagementWThread = PeerManagementThread(1, self.group_manager, 10)
        snipManagementWThread = SnipManagementThread(2, self.group_manager, self.snipManager)

        peerManagementWThread.start()
        snipManagementWThread.start()

        self.threads.append(peerManagementWThread)
        self.threads.append(snipManagementWThread)

        # time.sleep(30)
        # self.killThreads(threads)
        # self.kill()

        # Need to send self close message to interput recv from call
        while self.isAlive:
            if self.isAlive:
                data,addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                print(f"received message: {data} from: {addr}\n\n")

                if not data:
                    continue
                elif 'stop' in data:
                    print(f'stop {data}')
                    self.kill()

                elif 'snip' in data:
                    print(f'snip {data}')
                    snipData = data.split('snip')[1].split(' ')
                    print(snipData[0], snipData[1])
                    self.snipManager.add(snipData[1], snipData[0], addr)

                elif 'peer' in data:
                    print(f'peer {data}')
                    peerData = data[4:]
                    print(peerData)
                    self.group_manager.add(peerData)

                elif 'kill' in data:
                    print(f'kill {data}')
                    self.socket.close()
                    break

    def kill(self):
        print('killing gc and threads')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(
            bytes('kill', "utf-8"), self.socket.getsockname())
        sock.close()
        self.killThreads()
        self.isAlive = ''
    
    def killThreads(self):
        for t in self.threads:
            t.kill()
            t.join()



