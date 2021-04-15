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

        # 1. Current list of peers
        peers = self.group_manager.get_peers()
        report += f'{len(peers)}\n'
        for peer in peers:
           report += f'{str(peer.peer)} {peer.status.value}\n'

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

        # 6. all acks received
        acks_received = self.snipManager.get_acks()
        report += f'{len(acks_received)}\n'
        for ack in acks_received:
            reprot += f'{ack.peer} {ack.timestamp}\n'
        
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


process = Process('136.159.5.22', 55921)
process.start()