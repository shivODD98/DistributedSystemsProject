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
    def send(self, msg):
        sent = self.sock.send(msg.encode(self.FORMAT))
        if sent == 0:
            raise RuntimeError("socket connection broken")

    # Waits to recieve data in the socket and returns it as a string
    def receive(self):
        msg = self.sock.recv(1024).decode(self.FORMAT)
        if msg: 
            return str(msg)
        else:
            return ''


def handleTeamNameRequest():
    print('Team Name Request')

def handleCodeRequest():
    print('Code Request')

def handleReceiveRequest(data):
    lines = data.split('\n')
    nPeers = lines[1]
    print('Receive Request')

def handleReportRequest():
    print("Report Request")

socket = MySocket()
socket.connect('136.159.5.25', 55921)
while True:
    data = socket.receive()
    print(data)
    if not data:
        continue
    if re.search(data, Protocol["Team Name Request"]):
        handleTeamNameRequest()

    elif re.search(data, Protocol["Code Request"]):
        handleCodeRequest()

    elif re.search(data, Protocol["Receive Request"]):
        handleReceiveRequest(data)

    elif re.search(data, Protocol["Report Request"]):
        handleReportRequest()

    elif re.search(data, Protocol["Close Request"]):
        print("Close Request")
        socket.close()
        break