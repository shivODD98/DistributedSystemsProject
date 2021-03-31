from threading import Lock
import threading
from datetime import datetime
import sys

class Peer:
    """ Used to maintain peer instances and peer information """

    def __init__(self, peer, senderAddress):
        self.peer = peer
        self.senderAddress = senderAddress
        self.timer = threading.Timer(5*60, self.setNotActive).start()
        self.isActive = 1
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if senderAddress == '':
            self.from_registry = True
        else:
            self.from_registry = False

    def setNotActive(self):
        """ Sets instance of peer's status to not active """
        self.isActive = ''

    def resetTimer(self):
        """ Resets peer activity timer  """
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(5*60, self.setNotActive).start()


class GroupManager:
    """ Manages peers in our system that have communicated with the process"""

    def __init__(self):
        self.__list = []
        self.__sent_peers = []
        self.__received_peers = []
        self.mutex = Lock()
    
    def send_peer(self, peer, sent_to):
        """ Adds a new unique peer to __sent_peers list """
        peer = Peer(peer, sent_to)
        self.__sent_peers.append(peer)

    def received_peer(self, peer, source):
        """ Adds a new unique peer to __received_peers list """
        peer = Peer(peer, source)
        self.__received_peers.append(peer)

    def add(self, peerAddress, addr=''):
        """ Checks if peer is in list and resests that peers activity timer if so.
            If peer is not in list add a new unique peer to the list (Thread safe) """

        for i in range(len(self.__list)):
            if self.__list[i].peer == peerAddress:
                self.__list[i].resetTimer()
                return
        
        peer = Peer(peerAddress, addr)
        self.mutex.acquire()
        self.__list.append(peer)
        self.mutex.release()

    def get_peers(self):
        """ Get a list of all connected peers """
        return self.__list.copy()

    def get_received_peers(self):
        """ Get a list of all recieved peers """
        return self.__received_peers.copy()

    def get_sent_peers(self):
        """ Get a list of all sent peers """
        return self.__sent_peers.copy()
