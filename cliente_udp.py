import socket

HOST = 'localhost'
PORT = 50007
s = socket.socket(type=socket.SOCK_DGRAM)
s.sendto(b'Hello, world', (HOST, PORT))
data, from_addr = s.recvfrom(1024)
print('client received %r from %r' % (data, from_addr))
