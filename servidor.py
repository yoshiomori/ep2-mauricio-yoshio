import socket
from threading import Thread

HOST = ''
PORT = 50007


# Essa função roda em cada thread
def tcp_echo(conn, addr):
    print('Connected by ', addr)
    data = conn.recv(1024)
    conn.sendall(data)
    conn.close()


def tcp_server():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        Thread(target=tcp_echo, args=(conn, addr)).start()  # Cada conexão estabelecida gera uma thread


def udp_server():
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    while True:  # Servidor udp não precisa de threads pois lida da mesma forma cada pacote
        data, addr = s.recvfrom(1024)
        print('Connected by ', addr)
        s.sendto(data, addr)


tcp_thread = Thread(target=tcp_server)
udp_thread = Thread(target=udp_server)
tcp_thread.start()
udp_thread.start()
