from threading import Lock
import threading
from datetime import datetime
import sys
from enum import Enum
import socket

class PeerStatus(Enum):
    ALIVE = "alive"
    SILENT = "silent"
    MISSING_ACK = "missing_ack"

class Peer:
    """ Used to maintain peer instances and peer information """

    def __init__(self, peer, senderAddress, socket=None):
        self.peer = peer
        self.senderAddress = senderAddress
        self.timer = threading.Timer(5*60, self.setNotActive).start()
        self.status = PeerStatus.ALIVE
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ackTimer = threading.Timer(10, self.resendAck)
        self.resendMessage = ''
        self.retrys = 0
        self.socket = socket

        if senderAddress == '':
            self.from_registry = True
        else:
            self.from_registry = False

    def startAckTimer(self, resendMessage):
        self.resendMessage = resendMessage;
        self.ackTimer.start()

    def resendAck(self):
        """ Resends a message to a peer if ack was not received within a time period """
        self.retrys += 1

        print(f'retry sending message {self.retrys} (attempt: {resendMessage})')
        # Set peer to silent
        if self.retrys > 3:
            self.status = PeerStatus.SILENT
            self.ackTimer.cancel()
            return

        # Resend message
        address = self.peer.split(':')
        self.socket.sendto(bytes(self.resendMessage, "utf-8"), (f'{address[0]}', int(address[1])))

    def cancelAckTimer(self):
        self.ackTimer.cancel()
        self.retrys = 0

    def setPeerStatus(self, status):
        """ Sets instance of peer's status parameter status """
        self.status = status

    def setNotActive(self):
        """ Sets instance of peer's status to not active """
        self.status = PeerStatus.SILENT
    
    def setMessingAck(self):
        """ Sets instance of peer's status to missing ack """
        self.status = PeerStatus.MISSING_ACK

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
        self.socket = None
    
    def insertSocket(self, socket):
        self.socket = socket
        for peer in self.__list:
            peer.socket = socket

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
        
        peer = Peer(peerAddress, addr, self.socket)
        self.mutex.acquire()
        self.__list.append(peer)
        self.mutex.release()

    def received_ack(self, peerAddress):
        for i in range(len(self.__list)):
            if self.__list[i].peer == peerAddress:
                self.__list[i].cancelAckTimer()

    def awaitAcks(self, resendMessage):
        """ Sets all peers to missing ack status and sets a timer on them for retying """
        for peer in self.__list:
            if peer.status != PeerStatus.SILENT:
                peer.startAckTimer(resendMessage)

    def get_peers(self):
        """ Get a list of all connected peers """
        return self.__list.copy()

    def get_received_peers(self):
        """ Get a list of all recieved peers """
        return self.__received_peers.copy()

    def get_sent_peers(self):
        """ Get a list of all sent peers """
        return self.__sent_peers.copy()
