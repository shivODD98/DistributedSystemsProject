import socket
import time
from datetime import datetime
import threading
import sys
from GroupManager import PeerStatus

class SnipManagementThread(threading.Thread):
    """ Thread that handles sending snip messages to peers in the system """

    def __init__(self, threadId, group_manager, snipManager):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.group_manager = group_manager
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.snipManager = snipManager
        self.isAlive = 1

    def run(self):
        """ Starts loop that broadcasts user inputed snip messages"""
        print("Starting " + self.name)

        while self.isAlive:
            msgs = list(map(str, input(">").split()))
            msg = ''
            for ms in msgs:
                msg += ms + ' '
            if msg == 'exit':
                break
            if self.isAlive:
                self.broadcastSnip(msg)
    
    def broadcastSnip(self, msg):
        """ Broadcasts snip messages to peers in the system through socket"""
        peers = self.group_manager.get_peers()
        self.snipManager.clock.increment
        snipMsg = f'snip{self.snipManager.clock.getCounterValue()} {msg}'

        self.group_manager.awaitAcks(snipMsg)
        for peer in peers:
            sendToAdressInfo = peer.peer.split(':')
            if self.isAlive and peer.status != PeerStatus.SILENT:
                self.socket.sendto(bytes(snipMsg, "utf-8"), (f'{sendToAdressInfo[0]}', int(sendToAdressInfo[1])))

    def kill(self):
        """ Terminates SnipManagementThread and closes socket"""
        print('killing ' + self.name)
        self.isAlive = ''
        self.socket.close()
