import socket
import time
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
            msg = input("Please enter something: ")
            print("You entered: " + msg)
            self.broadcastSnip(msg)
    
    def broadcastSnip(self, msg):
        peers = self.group_manager.get_peers()

        for peer in peers:
            # if peer.isActive:
            print('sending message to ' + peer)
            sendToAdressInfo = peer.split(':')
            if self.isAlive:
                self.socket.sendto(
                    bytes(msg, "utf-8"), (f'{sendToAdressInfo[0]}', int(sendToAdressInfo[1])))

    def kill(self):
        self.isAlive = 0
        self.socket.close()
