import socket
import re

Protocol = {
    "Team Name Request": "get team name\n",
    "Code Request": "get code\n",
    "Receive Request": "receive peers\n",
    "Report Request": "get report\n",
    "Close Request": "close\n"
}

class MySocket:
    def __init__(self, sock=None):
        self.FORMAT = 'utf-8'
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    # Connects the socket to a host and port
    def connect(self, host, port):
        self.sock.connect((host, port))

    # Closes the socket
    def close(self):
        self.sock.close()

    # Sends a string message throught the socket encoded in utf-8
    def sendMsg(self, msg):
        sent = self.sock.send(msg.encode(self.FORMAT))
        if sent == 0:
            raise RuntimeError("socket connection broken")
        print('msg sent successfully')

    def sendFile(self, file_path):
        source_file = open(file_path, 'rb')
        source_data = source_file.read()
        sent = self.sock.send(source_data)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        source_file.close()
        print('source_data sent successfully')

    # Waits to recieve data in the socket and returns it as a string
    def receive(self):
        msg = self.sock.recv(1024).decode(self.FORMAT) # might have to increase recv chunk size
        if msg: 
            return str(msg)
        else:
            return ''

def handleTeamNameRequest(socket):
    print('Team Name Request')
    team_name = '2AM Design\n'
    socket.sendMsg(team_name)

def handleCodeRequest(socket):
    socket.sendMsg('Python\n')
    socket.sendFile('./client.py')
    socket.sendMsg('\n')
    socket.sendMsg('...\n')
    print('Code Request')

def handleReceiveRequest(data):
    lines = data.split('\n')
    nPeers = lines[1]
    print('Receive Request')

def handleReportRequest():
    print("Report Request")

socket = MySocket()
socket.connect('192.168.0.23', 55921)
while True:
    data = socket.receive()
    print(data)
    if not data:
        continue
    if re.search(data, Protocol["Team Name Request"]):
        handleTeamNameRequest(socket)

    elif re.search(data, Protocol["Code Request"]):
        handleCodeRequest(socket)

    elif re.search(data, Protocol["Receive Request"]):
        handleReceiveRequest(data)

    elif re.search(data, Protocol["Report Request"]):
        handleReportRequest()

    elif re.search(data, Protocol["Close Request"]):
        print("Close Request")
        socket.close()
        break
