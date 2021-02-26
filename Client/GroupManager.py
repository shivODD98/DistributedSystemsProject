from threading import Lock
import sys

class GroupManager:

    def __init__(self):
        self.__list = {} # A dictionary to avoid duplicates
        self.mutex = Lock()
    
    def add(self, peer):
        """ Adds a new unique peer to the list (Thread safe)"""
        self.mutex.acquire()
        self.__list[peer] = None
        self.mutex.release()

    def remove(self, peer):
        """ Removes a peer from the list if it exists(Thread safe)"""
        self.mutex.acquire()
        self.__list.pop(peer, None)
        self.mutex.release()

    def get_peers(self):
        """ Get a list of all connected peers """
        return list(self.__list.keys())