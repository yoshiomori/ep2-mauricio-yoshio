from socket import socket, SOCK_DGRAM
from threading import Semaphore


class ConexãoTCP(object):
    def __init__(self, conexão, endereço):
        self.conexão = conexão
        self.endereço = endereço

    def recebe(self):
        return self.conexão.recv(1024).decode()

    def envia(self, mensagem):
        self.conexão.send(mensagem.encode('unicode_escape'))

    def encerra(self):
        self.conexão.close()


class GerenciadorTCP(object):
    def __init__(self, porta):
        self.socket = socket()
        self.socket.bind(('', porta))
        self.socket.listen(1)

    def aceita(self):
        conexão = ConexãoTCP(*self.socket.accept())
        return conexão


class GerenciadorUDP(object):
    def __init__(self, porta):
        self.socket = socket(type=SOCK_DGRAM)
        self.socket.bind(('', porta))
        # novo_dado[endereço] armazena a informação de que chegou um novo dado para o serviço do endereço correspondente
        # dado_lido armazena a informação de que o último dado foi lido
        # nova_conexão armazena a informação de que chegou uma nova conexão
        # conexão_estabelecida armazenha a informação de que a última conexão foi estabelecida
        global novo_dado, dado_lido
        novo_dado = {}
        dado_lido = Semaphore()
        pass

    def aceita(self):
        # dado armazena a mensagem recebida no socket
        global dado, novo_dado, dado_lido
        while True:
            dado_lido.acquire()
            dado, endereço = self.socket.recvfrom(1024)
            # Envia a mensagem que chegou no socket para o serviço do endereço correspondente
            if endereço in novo_dado.keys():
                novo_dado[endereço].release()
            else:  # Ativa uma nova conexão
                novo_dado[endereço] = Semaphore()
                return ConexãoUDP(self.socket, endereço)
            pass


class ConexãoUDP(object):
    def __init__(self, conexão, endereço):
        self.conexão = conexão
        self.endereço = endereço

    def recebe(self):
        global dado, novo_dado, dado_lido
        novo_dado[self.endereço].acquire()
        mensagem = dado.decode()
        dado_lido.release()
        return mensagem

    def envia(self, mensagem):
        self.conexão.sendto(mensagem.encode('unicode_escape'), self.endereço)

    def encerra(self):
        global novo_dado
        novo_dado.pop(self.endereço)
