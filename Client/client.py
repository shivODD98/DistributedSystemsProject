import re
import asyncio
from datetime import datetime

ip_address = '192.168.1.97'
port_number = 55921

encoding = 'UTF-8'
Protocol = {
    "Team Name Request": "get team name\n",
    "Code Request": "get code\n",
    "Receive Request": "receive peers\n",
    "Report Request": "get report\n",
    "Close Request": "close\n"
}
Peers = []
Sources = []


class GroupCommunicator:

    def __init__(self):
        self.reader, self.writer = ''

    async def writeMsg(self, msg):
        self.writer.write(msg.encode(encoding))
        await self.writer.drain()

    async def writeFile(self, file_path):
        source_file = open(file_path, 'rb')
        source_data = source_file.read()
        source_file.close()
        self.writer.write(source_data)
        await self.writer.drain()

    def closeWriter(self):
        self.writer.close


async def handleTeamNameRequest(communicator):
    print('Team Name Request')
    team_name = '2AM Design\n'
    await communicator.writeMsg(team_name)

async def handleCodeRequest(communicator):
    print('Code Request')
    await communicator.writeMsg('Python\n')
    await communicator.writeFile('./client.py')
    await communicator.writeMsg('\n...\n')


async def handleReceiveRequest(communicator):
    print('Receive Request')
    nPeers = (await communicator.reader.readuntil(b'\n')).decode(encoding)
    nPeers = int(nPeers)

    for _ in range(nPeers):
        peer = (await communicator.reader.readuntil(b'\n')).decode(encoding)
        peer = peer.split('\n')[0]
        if peer not in Peers:
            Peers.append(peer)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    address = f'{ip_address}:{port_number}'
    if not list(filter(lambda source: source['Address'] == address, Sources)):
        Sources.append({
            "Address": address,
            "Date": date
        })
    print(Peers, Sources)


async def handleReportRequest(communicator):
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

async def client():
    communicator = GroupCommunicator()
    communicator.reader, communicator.writer = await asyncio.open_connection(ip_address, port_number)
    print('is connected')
    
    while True:
        data = await communicator.reader.readuntil(b'\n')
        data = data.decode(encoding)
        print(f"data is:{data}")
        if not data:
            continue
        if re.search(data, Protocol["Team Name Request"]):
            await handleTeamNameRequest(communicator)

        elif re.search(data, Protocol["Code Request"]):
            await handleCodeRequest(communicator)

        elif re.search(data, Protocol["Receive Request"]):
            await handleReceiveRequest(communicator)

        if re.search(data, Protocol["Report Request"]):
            await handleReportRequest(communicator)

        if re.search(data, Protocol["Close Request"]):
            print("Close Request")
            break

    communicator.closeWriter()


asyncio.run(client())
