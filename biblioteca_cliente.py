from cmd import Cmd
from socket import socket, SOCK_DGRAM


class Conexao(object):
    def __init__(self, tipo, ip, porta):
        if type(ip) is not str:
            raise RuntimeError('O ip não é válido.')
        if type(porta) is not int:
            raise RuntimeError('A porta não é válida.')
        hospedeiro = (ip, porta)
        if tipo is 'tcp':
            s = socket()
            s.connect(hospedeiro)
            self.envia = s.send

            def recebe():
                return s.recv(1024)
            self.recebe = recebe
        elif tipo is 'udp':
            s = socket(type=SOCK_DGRAM)

            def envia(mensagem):
                s.sendto(mensagem, hospedeiro)
            self.envia = envia

            def recebe():
                remetente = None
                mensagem = ''
                while remetente is not hospedeiro:
                    mensagem, remetente = s.recvfrom(1024)
                return mensagem
            self.recebe = recebe
        else:
            raise RuntimeError('O protocolo da camada de transporte %s não é suportado', tipo)
        self.encerra = s.close


class Estado(Cmd):
    prompt = '>'

    def __init__(self, conexao):
        super().__init__()
        if type(conexao) is not Conexao:
            raise RuntimeError('Argumento inválido!')
        self.conexao = conexao


class Logado(Estado):
    def do_logout(self):
        self.conexao.envia('logout')
        return 'deslogado'


class Deslogado(Estado):
    def do_login(self, nickname):
        self.conexao.envia(nickname)
        mensagem = self.conexao.recebe()
        if mensagem is not 'ok':
            print('O nickname %s não está registrado.' % nickname)
        elif mensagem is 'ok':
            return 'logado'

    def do_sair(self):
        self.conexao.encerra()
        return 'morto'
