Thu Mar 04 23:42:41 MST 2021
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
        await self.communicator.writeFile('./Client/client.py')
        await self.communicator.writeFile('./Client/GroupManager.py')
        await self.communicator.writeFile('./Client/Communicator/GroupCommunicator.py')
        await self.communicator.writeFile('./Client/Communicator/LogicalClock.py')
        await self.communicator.writeFile('./Client/Communicator/PeerManagementThread.py')
        await self.communicator.writeFile('./Client/Communicator/SnipManagementThread.py')
        await self.communicator.writeFile('./Client/Communicator/SnipManager.py')
        await self.communicator.writeMsg('\n...\n')

    async def handleReceiveRequest(self):
        print('Receive Request')
        nPeers = await self.communicator.readLine()
        nPeers = int(nPeers)

        for _ in range(nPeers):
            peer = await self.communicator.readLine()
            print(peer)
            peer = peer.split('\n')[0]
            self.group_manager.add(peer)

        # now = datetime.now()
        # date = now.strftime("%Y-%m-%d %H:%M:%S")
        # address = f'{ip_address}:{port_number}'
        # if not list(filter(lambda source: source['Address'] == address, Sources)):
        #     Sources.append({
        #         "Address": address,
        #         "Date": date
        #     })
        print(self.group_manager.get_peers())

    async def handleReportRequest(self):
        print("Report Request")

        await communicator.writeMsg(f'{len(Peers)}\n')
        for peer in Peers:
            await communicator.writeMsg(f'{peer}\n')

        await communicator.writeMsg(f'{len(Sources)}\n')

        for source in Sources:
            await communicator.writeMsg(f'{source["Address"]}\n')
            await communicator.writeMsg(f'{source["Date"]}\n')

            await communicator.writeMsg(f'{len(Peers)}\n')
            for peer in Peers:
                await communicator.writeMsg(f'{peer}\n')

    def startGroupCommunicator(self):
        self.groupCommunicator.start()
        
    async def run(self):
        # Initalize UDP server first to get location
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

            # elif re.search(data, self.Protocol["Report Request"]):
            #     await handleReportRequest(communicator)

            elif re.search(data, self.Protocol["Close Request"]):
                print("Close Request")
                break
        self.communicator.closeWriter()

        # start group communicator on new thread (maybe pass group manager into it?)
        t = threading.Thread(target=self.startGroupCommunicator)
        t.start()
        time.sleep(60)
        self.groupCommunicator.kill()
        t.join()
        # Use a while loop to check and see if the gc thread is alive or not anymore and then shutdown whatever here too       
        # while self.groupCommunicator.isAlive:
            
        print("back to main client")
        # need to kill asyncio socket to

    def start(self):
        asyncio.run(self.run())


process = Process('192.168.1.89', 55921)
process.start()


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
import re
import socket
import time
from Communicator.SnipManagementThread import SnipManagementThread
from Communicator.PeerManagementThread import PeerManagementThread
from Communicator.SnipManager import SnipManager

class GroupCommunicator:

    def __init__(self, group_manager, snipManager):
        # self.server_ip = server_ip
        # self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.group_manager = group_manager
        self.snipManager = snipManager
        self.isAlive = 1
        self.threads = []

    def initalize(self, queueLength = 10):
        # Start a socket server to listen on a free port that is to be determined
        self.socket.bind((socket.gethostname(), 0))

        return self.socket.getsockname()

    # TODO: need to make this on a new thread because it completly hangs the console
    def start(self):

        print("UDP server is starting...")
        peerManagementWThread = PeerManagementThread(1, self.group_manager, 10)
        snipManagementWThread = SnipManagementThread(2, self.group_manager, self.snipManager)

        peerManagementWThread.start()
        snipManagementWThread.start()

        self.threads.append(peerManagementWThread)
        self.threads.append(snipManagementWThread)

        # time.sleep(30)
        # self.killThreads(threads)
        # self.kill()

        # Need to send self close message to interput recv from call
        while self.isAlive:
            if self.isAlive:
                data,addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                print(f"received message: {data} from: {addr}\n\n")

                if not data:
                    continue
                elif 'stop' in data:
                    print(f'stop {data}')
                    self.kill()

                elif 'snip' in data:
                    print(f'snip {data}')
                    snipData = data.split('snip')[1].split(' ')
                    print(snipData[0], snipData[1])
                    self.snipManager.add(data[6:], snipData[0], addr)

                elif 'peer' in data:
                    print(f'peer {data}')
                    peerData = data[4:]
                    print(peerData)
                    self.group_manager.add(peerData, addr)

                elif 'kill' in data:
                    print(f'kill {data}')
                    self.socket.close()
                    break

    def kill(self):
        print('killing gc and threads')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(
            bytes('kill', "utf-8"), self.socket.getsockname())
        sock.close()
        self.killThreads()
        self.isAlive = ''
    
    def killThreads(self):
        for t in self.threads:
            t.kill()
            t.join()



import sys


class LogicalClock:

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

class PeerManagementThread(threading.Thread):

    def __init__(self, threadId, group_manager, interval):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.group_manager = group_manager
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.interval = interval
        self.isAlive = 1

    def run(self):
        print("Starting " + self.name)
        while self.isAlive:
            time.sleep(self.interval)
            self.sendPeerMsg()
    
    def sendPeerMsg(self):
        peers = self.group_manager.get_peers()
        peerInfo = peers[random.randint(0, (len(peers)-1))].peer
        for peer in peers:
            if peer.isActive:
            # print('sending message to ' + peer)
                msg = f'peer{peerInfo}'
                sendToAdressInfo = peer.peer.split(':')
                if self.isAlive:
                    self.socket.sendto(
                        bytes(msg, "utf-8"), (f'{sendToAdressInfo[0]}', int(sendToAdressInfo[1])))

    def kill(self):
        print('killing ' + self.name)
        self.isAlive = ''
        self.socket.close()

    

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
            # msg = input("> ") # need to stop this in shutdown process
            msgs = list(map(str, input(">").split()))
            print(msgs)
            msg = ''
            for ms in msgs:
                msg += ms + ' '
            print(msg)
            if msg == 'exit':
                break
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
import sys
from Communicator.LogicalClock import LogicalClock
from datetime import datetime

class Snip:

    def __init__(self, msg, timestamp, sender):
        self.snip_msg = msg
        self.timestamp = timestamp
        self.sender = sender
        self.date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

class SnipManager:

    def __init__(self):
        self.clock = LogicalClock()
        self.__message_list = []

    # def sendUserMsg(self, msg):
    #     """ Sends a new user message to all connected peers (Thread safe)"""
    #     self.__message_list.append(msg)
    
    # def getUsersMsg(self):
    #     """ gets and waits for user input to console """
    #     # https: // stackoverflow.com/questions/70797/how-to-prompt-for-user-input-and-read-command-line-arguments
    #     self.__message_list.append('')

    def add(self, msg, timestamp, sender):
        """ Adds a new message to the list (Thread safe)"""
        self.clock.updateToValue(max(self.clock.getCounterValue(), int(timestamp)))
        print(msg)
        snip = Snip(msg, timestamp, sender)
        self.__message_list.append(snip)
        self.clock.increment()
        self.print_msgs()

    def get_msgs(self):
        """ Get a list of all messages sent and recieved in order """
        return self.__message_list.copy()

    def print_msgs(self):
        print('\n\n')
        print('Timestamp:   |   Message:\n')
        for msg in self.__message_list:
            print('--------------------------\n')
            print(f'{msg.timestamp}             {msg.snip_msg}')
            print('--------------------------\n')
        print('\n\n')

