import re
import asyncio
from datetime import datetime
from GroupManager import GroupManager

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

    async def handleTeamNameRequest(self):
        print('Team Name Request')
        team_name = '2AM Design\n'
        await self.communicator.writeMsg(team_name)

    async def handleLocationRequest(self):
        print('Location Request')
        location = '10.58.192.238:65231\n'
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

    async def run(self):
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
                await self.handleLocationRequest()

            elif re.search(data, self.Protocol["Code Request"]):
                await self.handleCodeRequest()

            elif re.search(data, self.Protocol["Receive Request"]):
                await self.handleReceiveRequest()

            # elif re.search(data, self.Protocol["Report Request"]):
            #     await handleReportRequest(communicator)

            elif re.search(data, self.Protocol["Close Request"]):
                print("Close Request")
                break

        communicator.closeWriter()


    def start(self):
        asyncio.run(self.run())

process = Process('136.159.5.22', 55921)
process.start()

Peers = []
Sources = []

