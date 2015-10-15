from socket import socket, SOCK_DGRAM


class Conexão(object):
    def __init__(self, tipo, ip, porta):
        if type(ip) is not str:
            raise RuntimeError('O ip não é válido.')
        if type(porta) is not int:
            raise RuntimeError('A porta não é válida.')
        self.hospedeiro = (ip, porta)
        if tipo == 'tcp':
            self.socket = socket()
            self.socket.connect(self.hospedeiro)
        elif tipo == 'udp':
            self.socket = socket(type=SOCK_DGRAM)
        else:
            raise RuntimeError('O tipo de protocolo não é suportado.')
        self.tipo = tipo

    def envia(self, mensagem):
        if self.tipo == 'tcp':
            self.socket.send(mensagem.encode('unicode_escape'))
        else:
            self.socket.sendto(mensagem.encode('unicode_escape'), self.hospedeiro)

    def recebe(self):
        return self.socket.recv(1024).decode()

    def encerra(self):
        if self.tipo == 'tcp':
            self.socket.close()
