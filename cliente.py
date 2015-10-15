from sys import argv
from biblioteca_cliente import Conexão


def cliente():
    if len(argv) < 4:
        raise RuntimeError('Falta argumentos!')
    conexão = Conexão(argv[1], argv[2], int(argv[3]))
    while True:
        mensagem = input('> ')
        conexão.envia(mensagem)
        resposta = conexão.recebe()
        print(resposta)
if __name__ == '__main__':
    cliente()
