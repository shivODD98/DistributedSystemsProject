import socket
import random
import time
import threading
import sys

class PeerManagementThread(threading.Thread):
    """ Thread that handles sending peer messages to active peers in the system """

    def __init__(self, threadId, group_manager, interval):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.group_manager = group_manager
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.interval = interval
        self.isAlive = 1

    def run(self):
        """ Starts loop that sends interval messages to peers in the system """
        print("Starting " + self.name)
        while self.isAlive:
            time.sleep(self.interval)
            self.sendPeerMsg()
    
    def sendPeerMsg(self):
        """" Sends message to active peers in the system through socket"""
        peers = self.group_manager.get_peers()
        peerInfo = peers[random.randint(0, (len(peers)-1))].peer
        for peer in peers:
            if peer.isActive:
                self.group_manager.send_peer(peerInfo, peer.peer)
                msg = f'peer{peerInfo}'
                sendToAdressInfo = peer.peer.split(':')
                if self.isAlive:
                    self.socket.sendto(
                        bytes(msg, "utf-8"), (f'{sendToAdressInfo[0]}', int(sendToAdressInfo[1])))

    def kill(self):
        """ Terminates PeerManagementThread and closes socket"""
        print('killing ' + self.name)
        self.isAlive = ''
        self.socket.close()

    

