import socket

HOST = 'localhost'
PORT = 50007
s = socket.socket()
s.connect((HOST, PORT))
s.sendall(b'Hello, world')
data = s.recv(1024)
s.close()
print('Received', repr(data))
