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

async def writeMsg(writer, msg):
    writer.write(msg.encode(encoding))
    await writer.drain()

async def writeFile(writer, file_path):
    source_file = open(file_path, 'rb')
    source_data = source_file.read()
    source_file.close()
    writer.write(source_data)
    await writer.drain()

async def handleTeamNameRequest(writer):
    print('Team Name Request')
    team_name = '2AM Design\n'
    await writeMsg(writer, team_name)

async def handleCodeRequest(writer):
    print('Code Request')
    await writeMsg(writer, 'Python\n')
    await writeFile(writer, './client.py')
    await writeMsg(writer, '\n...\n')

async def handleReceiveRequest(reader):
    print('Receive Request')
    nPeers = (await reader.readuntil(b'\n')).decode(encoding)
    nPeers = int(nPeers)

    for _ in range(nPeers):
        peer = (await reader.readuntil(b'\n')).decode(encoding)
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


async def handleReportRequest(writer):
    print("Report Request")

    await writeMsg(writer, f'{len(Peers)}\n')
    for peer in Peers:
        await writeMsg(writer, f'{peer}\n')

    await writeMsg(writer, f'{len(Sources)}\n')

    for source in Sources:
        await writeMsg(writer, f'{source["Address"]}\n')
        await writeMsg(writer, f'{source["Date"]}\n')

        await writeMsg(writer, f'{len(Peers)}\n')
        for peer in Peers:
            await writeMsg(writer, f'{peer}\n')
    


async def client():
    reader, writer = await asyncio.open_connection(ip_address, port_number)
    print('is connected')
    
    while True:
        data = await reader.readuntil(b'\n')
        data = data.decode(encoding)
        print(f"data is:{data}")
        if not data:
            continue
        if re.search(data, Protocol["Team Name Request"]):
            await handleTeamNameRequest(writer)

        elif re.search(data, Protocol["Code Request"]):
            await handleCodeRequest(writer)

        elif re.search(data, Protocol["Receive Request"]):
            await handleReceiveRequest(reader)

        if re.search(data, Protocol["Report Request"]):
            await handleReportRequest(writer)

        if re.search(data, Protocol["Close Request"]):
            print("Close Request")
            break

    writer.close()


asyncio.run(client())
