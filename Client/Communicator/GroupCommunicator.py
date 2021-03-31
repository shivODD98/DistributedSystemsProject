import re
import socket
import time
from Communicator.SnipManagementThread import SnipManagementThread
from Communicator.PeerManagementThread import PeerManagementThread
from Communicator.SnipManager import SnipManager

class GroupCommunicator:
    """ Used to handle all incoming peer and snip messages """

    def __init__(self, group_manager, snipManager):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.group_manager = group_manager
        self.snipManager = snipManager
        self.isAlive = 1
        self.threads = []

    def initalize(self, queueLength = 10):
        """ Start a socket server to listen on a free port that is to be determined """
        self.socket.bind((socket.gethostname(), 0))
        hostName = self.socket.getsockname()
        self.group_manager.add(f'{hostName[0]}:{hostName[1]}','')
        return hostName

    def start(self):
        """ Thread function that creates and starts threads that handle snip messages and peer messages. 
            Terminates system when recieves 'stop' message """
        
        print("UDP server is starting...")
        peerManagementWThread = PeerManagementThread(1, self.group_manager, 10)
        snipManagementWThread = SnipManagementThread(2, self.group_manager, self.snipManager)

        peerManagementWThread.start()
        snipManagementWThread.start()

        self.threads.append(peerManagementWThread)
        self.threads.append(snipManagementWThread)

        while self.isAlive:
            if self.isAlive:
                data,addr = self.socket.recvfrom(1024)
                sourcePeer = f'{addr[0]}:{addr[1]}'
                data = data.decode('utf-8')

                if not data:
                    continue
                elif 'stop' in data:
                    # send 'ack' to socket (registry), then kill
                    self.socket.sendto(bytes("ack2AM Design", "utf-8"), (f'{addr[0]}', int(addr[1])))
                    self.kill()

                elif 'snip' in data:
                    snipData = data.split('snip')[1].split(' ')
                    self.snipManager.add(data[6:], snipData[0], sourcePeer)

                elif 'peer' in data:
                    peerData = data[4:]
                    self.group_manager.add(peerData, sourcePeer)
                    self.group_manager.received_peer(peerData, sourcePeer)

                elif 'kill' in data:
                    self.socket.close()
                    break

    def kill(self):
        """ Terminates all active threads and closes socket """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(
            bytes('kill', "utf-8"), self.socket.getsockname())
        sock.close()
        self.killThreads()
        self.isAlive = ''
    
    def killThreads(self):
        """ Terminates all threads """
        for t in self.threads:
            t.kill()
            t.stop()
            t.join()



