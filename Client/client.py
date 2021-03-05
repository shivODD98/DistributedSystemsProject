import re
import asyncio
import threading
from datetime import datetime
from GroupManager import GroupManager
from Communicator.GroupCommunicator import GroupCommunicator
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
        self.groupCommunicator = GroupCommunicator(self.group_manager)

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

#OLD
Peers = []
Sources = []
# python client/client.py

