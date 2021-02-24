from threading import Lock
import sys

class GroupManager:

    def __init__(self):
        self.__list = []
        self.mutex = Lock()
    
    def add(self, peer):
        """ Adds a new peer to the list (Thread safe)"""
        self.mutex.acquire()
        self.__list.append(peer)
        self.mutex.release()

    def remove(self, peer):
        """ Removes a peer from the list (Thread safe)"""
        self.mutex.acquire()
        self.__list.remove(peer)
        self.mutex.release()

    def get_peers(self):
        """ Get a list of all connected peers """
        return self.__list.copy()