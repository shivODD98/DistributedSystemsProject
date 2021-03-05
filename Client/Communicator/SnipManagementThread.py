import socket
import time
from datetime import datetime
import threading
import sys

class SnipManagementThread(threading.Thread):

    def __init__(self, threadId, group_manager, snipManager):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.group_manager = group_manager
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.snipManager = snipManager
        self.isAlive = 1

    def run(self):
        print("Starting " + self.name)
        while self.isAlive:
            msg = input("Please enter something: ") # need to stop this in shutdown process
            if self.isAlive:
                self.broadcastSnip(msg)
    
    def broadcastSnip(self, msg):
        peers = self.group_manager.get_peers()

        self.snipManager.clock.increment
        for peer in peers:
            print('sending message to ' + peer.peer)
            sendToAdressInfo = peer.peer.split(':')
            snipMsg = f'snip{self.snipManager.clock.getCounterValue()} {msg}'
            if self.isAlive:
                self.socket.sendto(
                    bytes(snipMsg, "utf-8"), (f'{sendToAdressInfo[0]}', int(sendToAdressInfo[1])))

    def kill(self):
        print('killing ' + self.name)
        self.isAlive = ''
        self.socket.close()
