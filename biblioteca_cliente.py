from socket import socket, SOCK_DGRAM


class Conexao(object):
    def __init__(self, tipo, ip, porta):
        if type(ip) is not str:
            raise RuntimeError('O ip não é válido.')
        if type(porta) is not int:
            raise RuntimeError('A porta não é válida.')
        hospedeiro = (ip, porta)
        if tipo == 'tcp':
            s = socket()
            s.connect(hospedeiro)

            def envia(mensagem):
                s.send(mensagem.encode('unicode_escape'))
            self.envia = envia
            self.encerra = s.close()
        elif tipo == 'udp':
            s = socket(type=SOCK_DGRAM)

            def envia(mensagem):
                s.sendto(mensagem.encode('unicode_escape'), hospedeiro)
            self.envia = envia
            self.encerra = lambda: None
        else:
            raise RuntimeError('O tipo de protocolo não é suportado.')

        def recebe():
            mensagem = s.recv(1024)
            return mensagem.decode()
        self.recebe = recebe


class Estado(object):
    intro = 'Digite ? para informação'
    prompt = '> '

    def __init__(self, conexao):
        if type(conexao) is not Conexao:
            raise RuntimeError('Argumento inválido!')
        self.conexao = conexao

    def rodando(self):
        while True:
            mensagem = input(self.prompt)
            comando, sep, resto = mensagem.partition(' ')
            if comando not in self.__dir__():
                print('%s não é um comando válido' % comando)
            else:
                function = self.__getattribute__(comando)
                try:
                    if resto != '':
                        return function(*resto.split(' '))  # * transforma a lista resultante do split em argumentos
                    else:
                        return function()
                except TypeError:
                    print('Argumentos não são válidos.')


class Logado(Estado):
    def logout(self):
        self.conexao.envia('logout')
        return 'deslogado'


class Deslogado(Estado):
    def login(self, nickname):
        self.conexao.envia(nickname)
        mensagem = self.conexao.recebe()
        if mensagem == 'nok':
            print('O nickname %s não está registrado.' % nickname)
        elif mensagem == 'ok':
            return 'logado'
        else:
            raise RuntimeError('Estado não desejável.')

    def sair(self):
        self.conexao.encerra()
        return 'morto'
