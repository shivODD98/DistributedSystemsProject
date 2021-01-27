import socket

class MySocket:
    def __init__(self, sock=None):
        print('init')
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()

    def send(self, msg):
        totalsent = 0
        # while totalsent < MSGLEN:
            # sent = self.sock.send(msg[totalsent:])
        sent = self.sock.send(msg.encode('utf-8'))
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

    def receive(self):
        chunks = []
        bytes_recd = 0
        # while bytes_recd < MSGLEN:
        # chunk = self.sock.recv (min(MSGLEN - bytes_recd, 2048))
        chunk = self.sock.recv(1024)
        if chunk == b'':
            chunks = "exit"
            return chunks 
            # raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
        
socket = MySocket()
socket.connect('192.168.0.23', 55921)
while True:
            data = socket.receive()
            print(data)
            if not data:
                continue
            if data == b'get id\n':
                print('get id')
                socket.send('30031173\n')
                # break
            if data == b'get name\n':
                print('get name')
                socket.send('Shiv Odedra\n')
                # break
            if data == "exit":
                print('closing socket')
                socket.close()
                break