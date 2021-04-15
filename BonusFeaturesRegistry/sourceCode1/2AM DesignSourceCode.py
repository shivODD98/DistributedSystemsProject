Wed Apr 14 23:23:55 MDT 2021
py
import re
import asyncio
import threading
from datetime import datetime
from GroupManager import GroupManager
from Communicator.GroupCommunicator import GroupCommunicator
from Communicator.SnipManager import SnipManager
import time

# Helper class for communicating through a channel
class ChannelCommunicator:

    def __init__(self, encoding = 'UTF-8'):
        self.reader = ''
        self.writer = ''
        self.encoding = encoding

    async def readLine(self):
        data = await self.reader.readuntil(b'\n')
        return data.decode(self.encoding)

    async def writeMsg(self, msg):
        self.writer.write(msg.encode(self.encoding))
        await self.writer.drain()

    async def writeFile(self, file_path):
        source_file = open(file_path, 'rb')
        source_data = source_file.read()
        source_file.close()
        self.writer.write(source_data)
        await self.writer.drain()

    def closeWriter(self):
        self.writer.close()


class Process:

    Protocol = {
        "Team Name Request": "get team name\n",
        "Get Location Request": "get location\n",
        "Code Request": "get code\n",
        "Receive Request": "receive peers\n",
        "Report Request": "get report\n",
        "Close Request": "close\n"
    }

    def __init__(self, registry_ip, registry_port, encoding = 'UTF-8'):
        self.registry_ip = registry_ip
        self.registry_port = registry_port
        self.encoding = encoding
        self.received_timestamp = ''
        self.communicator = ChannelCommunicator()
        self.group_manager = GroupManager()
        self.snipManager = SnipManager()
        self.groupCommunicator = GroupCommunicator(
            self.group_manager, self.snipManager)
        


    async def handleTeamNameRequest(self):
        print('Team Name Request')
        team_name = '2AM Design\n'
        await self.communicator.writeMsg(team_name)

    async def handleLocationRequest(self, udp_address):
        print('Location Request')
        location = f'{udp_address[0]}:{udp_address[1]}\n'
        await self.communicator.writeMsg(location)

    async def handleCodeRequest(self):
        print('Code Request')
        await self.communicator.writeMsg('py\n')
        await self.communicator.writeFile('../Client/client.py')
        await self.communicator.writeFile('../Client/GroupManager.py')
        await self.communicator.writeFile('../Client/Communicator/GroupCommunicator.py')
        await self.communicator.writeFile('../Client/Communicator/LogicalClock.py')
        await self.communicator.writeFile('../Client/Communicator/PeerManagementThread.py')
        await self.communicator.writeFile('../Client/Communicator/SnipManagementThread.py')
        await self.communicator.writeFile('../Client/Communicator/SnipManager.py')
        await self.communicator.writeMsg('\n...\n')

    async def handleReceiveRequest(self):
        print('Receive Request')
        self.received_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nPeers = await self.communicator.readLine()
        nPeers = int(nPeers)
        print(nPeers)
        for _ in range(nPeers):
            peer = await self.communicator.readLine()
            print(peer)
            peer = peer.split('\n')[0]
            self.group_manager.add(peer)


    async def handleReportRequest(self):
        print("Report Request")

        report = ''
        peers = self.group_manager.get_peers()
        # 1. Current list of peers
        report += f'{len(peers)}\n'
        for peer in peers:
           report += f'{str(peer.peer)}\n'

        # 2. peer list sources
        report += f'1\n'
        report += f'{self.registry_ip}:{self.registry_port}\n'
        report += f'{self.received_timestamp}\n'

        registry_peers = [peer for peer in peers if peer.from_registry]
        report += f'{len(registry_peers)}\n'
        for peer in registry_peers:
            if peer.from_registry:
                report += f'{peer.peer}\n'

        # 3. all peers received from udp
        received_peers = self.group_manager.get_received_peers()
        report += f'{len(received_peers)}\n'
        for peer in received_peers:
            report += f'{peer.senderAddress} {peer.peer} {peer.timestamp}\n'
        
        # 4. all peers sent through udp
        sent_peers = self.group_manager.get_sent_peers()
        report += f'{len(sent_peers)}\n'
        for peer in sent_peers:
            report += f'{peer.senderAddress} {peer.peer} {peer.timestamp}\n'

        # 5. all snippets received, in timestamp order
        snippets = self.snipManager.get_msgs()
        report += f'{len(snippets)}\n'
        for snippet in snippets:
            report += f'{snippet.timestamp} {snippet.snip_msg} {snippet.sender}\n'
        # send report
        await self.communicator.writeMsg(report)
        print(report)

    def startGroupCommunicator(self):
        self.groupCommunicator.start()
        
    async def run(self):
        isShuttingDown = False
        udp_address = self.groupCommunicator.initalize()
        print(f"UDP server initalized on {udp_address}")
        
        self.communicator.reader, self.communicator.writer = await asyncio.open_connection(self.registry_ip, self.registry_port)
        print('is connected')
        
        while True:
            data = await self.communicator.readLine()

            print(f"data is:{data}")
            if not data:
                continue
            elif re.search(data, self.Protocol["Team Name Request"]):
                await self.handleTeamNameRequest()
            
            elif (re.search(data, self.Protocol["Get Location Request"])):
                await self.handleLocationRequest(udp_address)

            elif re.search(data, self.Protocol["Code Request"]):
                await self.handleCodeRequest()

            elif re.search(data, self.Protocol["Receive Request"]):
                await self.handleReceiveRequest()

            elif re.search(data, self.Protocol["Report Request"]):
                await self.handleReportRequest()

            elif re.search(data, self.Protocol["Close Request"]):
                print("Close Request")
                if isShuttingDown:
                    print("2nd communication ended with registry")
                    break;
    
                self.communicator.closeWriter()
                t = threading.Thread(target=self.startGroupCommunicator)
                t.start()
                t.join()
                isShuttingDown = True
                self.communicator.reader, self.communicator.writer = await asyncio.open_connection(self.registry_ip, self.registry_port)


            
    def start(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.run())
        # asyncio.run(self.run())


process = Process('192.168.1.89', 55921)
process.start()
from threading import Lock
import threading
from datetime import datetime
import sys
from enum import Enum

class PeerStatus(Enum):
    ALIVE= "alive"
    SILENT= "silent"
    MISSING_ACK= "missing_ack"

class Peer:
    """ Used to maintain peer instances and peer information """

    def __init__(self, peer, senderAddress):
        self.peer = peer
        self.senderAddress = senderAddress
        self.timer = threading.Timer(5*60, self.setNotActive).start()
        self.status = PeerStatus.ALIVE
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if senderAddress == '':
            self.from_registry = True
        else:
            self.from_registry = False

    def setPeerStatus(self, status):
        """ Sets instance of peer's status parameter status """
        self.status = status

    def setNotActive(self):
        """ Sets instance of peer's status to not active """
        self.status = PeerStatus.SILENT

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
                    # send 'ack' to socket (peer)
                    self.socket.sendto(bytes(f"ack {snipData[0]}", "utf-8"), (f'{addr[0]}', int(addr[1])))
                    self.snipManager.add(data[6:], snipData[0], sourcePeer)
                
                elif 'ctch' in data:
                    snipData = data.split('ctch')[1].split(' ', 2)
                    originalSender = snipData[0]
                    timestamp = snipData[1]
                    content = snipData[2]
                    self.snipManager.addCtchSnip(originalSender, timestamp, content)

                elif 'ack' in data:
                    # ack for a snip received
                    timestamp = data.split(' ')[1]
                    self.snipManager.add_ack(sourcePeer, timestamp)

                elif 'peer' in data:
                    peerData = data[4:]
                    self.group_manager.add(peerData, sourcePeer)
                    self.group_manager.received_peer(peerData, sourcePeer)
                    self.sendPeerAllSnips(addr)

                elif 'kill' in data:
                    self.socket.close()
                    break

    def sendPeerAllSnips(self, addr):
        """ Handles ctch message by sending approapiate peer all known snip messages """
        snippets = self.snipManager.get_msgs()
        for snip in snippets:
            self.socket.sendto(
                bytes(
                    f"ctch{snip.sender} {snip.timestamp} {snip.snip_msg}", "utf-8"),
                    (f'{addr[0]}', int(addr[1])
                )
            )

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



import sys


class LogicalClock:
    """ Used to maintain logical clock """

    def __init__(self):
        self.counter = 0

    def increment(self):
        """ Increments Logical Clock by one"""
        self.counter = self.counter + 1

    def updateToValue(self, val):
        """ Update Logical Clocks counter to specific value """
        self.counter = val

    def getCounterValue(self):
        """ Get the logical clocks ounter value """
        return self.counter
import socket
import random
import time
import threading
import sys
# from ..Client.GroupManager import PeerStatus

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
            if peer.status == 'alive':
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

    

import socket
import time
from datetime import datetime
import threading
import sys

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
        for peer in peers:
            sendToAdressInfo = peer.peer.split(':')
            snipMsg = f'snip{self.snipManager.clock.getCounterValue()} {msg}'
            if self.isAlive:
                self.socket.sendto(
                    bytes(snipMsg, "utf-8"), (f'{sendToAdressInfo[0]}', int(sendToAdressInfo[1])))

    def kill(self):
        """ Terminates SnipManagementThread and closes socket"""
        print('killing ' + self.name)
        self.isAlive = ''
        self.socket.close()
import sys
from Communicator.LogicalClock import LogicalClock
from datetime import datetime

class Snip:
    """ Used to maintain snip instances and snip information """

    def __init__(self, msg, timestamp, sender):
        self.snip_msg = msg
        self.timestamp = timestamp
        self.sender = sender
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Ack:
    def __init__(self, peer, timestamp):
        self.timestamp = timestamp
        self.peer = peer

class SnipManager:
    """ Manages snips from and to our process """

    def __init__(self):
        self.clock = LogicalClock()
        self.__message_list = []
        self.__ack_list = []

    def add(self, msg, timestamp, sender):
        """ Adds a new snip message to the list (Thread safe), updates logical clock and displays snip messages """
        self.clock.updateToValue(max(self.clock.getCounterValue(), int(timestamp)))
        snip = Snip(msg, timestamp, sender)
        self.__message_list.append(snip)
        self.clock.increment()
        self.print_msgs()

    def add_ack(self, peer, timestamp):
        ack = Ack(peer, timestamp)
        self.__ack_list.append(ack)

    def get_msgs(self):
        """ Get a list of all messages sent and recieved in order """
        snippets = self.__message_list.copy()
        snippets.sort(reverse=False, key =lambda x: int(x.timestamp))
        return snippets

    def get_acks(self):
        acks = self.__ack_list.copy()
        return acks

    def addCtchSnip(self, originalSender, timestamp, content):
        """ Checks is recieved snip message is a duplicate before adding to list of snips """
        for snip in self.__message_list:
            if snip.sender == originalSender and snip.timestamp == timestamp:
                return
        self.add(content, timestamp, originalSender)

    def print_msgs(self):
        """ Formats and prints snip messages """
        messages = self.get_msgs()
        print(messages)
        print('\n\n')
        print('Timestamp:   |   Message:\n')
        for msg in messages:
            print('--------------------------\n')
            print(f'{msg.timestamp}             {msg.snip_msg}')
            print('--------------------------\n')
        print('\n\n')

