from threading import Lock
import threading
from datetime import datetime
import sys

class Peer:
    def __init__(self, peer, senderAddress):
        self.peer = peer
        self.senderAddress = senderAddress
        self.timer = threading.Timer(120.0, self.setNotActive).start()
        self.isActive = 1
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def setNotActive(self):
        self.isActive = ''

    def resetTimer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(60.0, self.setNotActive).start()

class GroupManager:

    def __init__(self):
        self.__list = [] # A dictionary to avoid duplicates
        self.mutex = Lock()
    
    def add(self, peerAddress, addr=''):
        """ Adds a new unique peer to the list (Thread safe)"""

        for i in range(len(self.__list)):
            if self.__list[i].peer == peerAddress:
                self.__list[i].resetTimer()
                return
        
        peer = Peer(peerAddress, addr)
        self.mutex.acquire()
        self.__list.append(peer)
        self.mutex.release()

    # def remove(self, peer):
    #     """ Removes a peer from the list if it exists(Thread safe)"""
    #     self.mutex.acquire()
    #     self.__list.pop(peer, None)
    #     self.mutex.release()

    def get_peers(self):
        """ Get a list of all connected peers """
        return self.__list
