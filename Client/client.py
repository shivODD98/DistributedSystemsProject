import socket

Protocol = {
    "Team Name Request": "get team name\n",
    "Code Request": "get code\n",
    "Receive Request": "receive peers\n"
    "Report Request": "get report\n",
    "Close Request": "close\n"
}

class MySocket:
    def __init__(self, sock=None):
        print('init')
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
        totalsent = 0
        sent = self.sock.send(msg.encode(self.FORMAT))
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

    # Waits to recieve data in the socket and returns it as a string
    def receive(self):
        msg = self.sock.recv(1024).decode(self.FORMAT)
        if msg: 
            return str(msg)
        else:
            return ''
        
socket = MySocket()
socket.connect('192.168.0.23', 55921)
while True:
    data = socket.receive()
    print(data)
    if not data:
        continue
    if data == 'get id\n':
        print('get id')
        socket.send('30031173\n')
        # break
    if data == 'get name\n':
        print('get name')
        socket.send('Shiv Odedra\n')
        # break
    if data == 'close':
        print('closing socket')
        socket.close()
        break