from sys import argv
from biblioteca_cliente import Conexão
from threading import Thread

estado = 'rodando'


def prompt_servidor(conexão):
    global estado
    while estado == 'rodando':
        print('Digite comando:')
        mensagem = input()
        if mensagem == 'sair':
            estado = 'fim'
        conexão.envia(mensagem)


def interpreta_resposta(argumento):
    if int(argumento) == 0:
        print('Comando inválido!')
    elif int(argumento) == 1:
        print('Comando inválido! Aguardando senha.')
    elif int(argumento) == 2:
        print('Usuário inválido.')
    elif int(argumento) == 3:
        print('Usuário em uso!')
    elif int(argumento) == 4:
        print('Aguardando senha.')
    elif int(argumento) == 5:
        print('Nome de usuário cadastrado com sucesso!')
    elif int(argumento) == 6:
        print('Tchau!')
    elif int(argumento) == 7:
        print('Logado')
    elif int(argumento) == 8:
        print('Convite enviado para o jogador!')
    elif int(argumento) == 9:
        print('Você é o X')
    elif int(argumento) == 10:
        print('Você não aceitou a partida.')
    elif int(argumento) == 11:
        print('Bem vindo à casa Véia!')
    elif int(argumento) == 12:
        print('Saiu do jogo com sucesso!')
    else:
        print('Servidor enviou uma respota desconhecida')
        pass
    pass


def interpreta_resposta_argumento(argumento):
    num, sep, argumento = argumento.partition(' ')
    if int(num) == 0:
        print('%s perdeu a conexão! Partida cancelada!' % argumento)
    elif int(num) == 1:
        print('%s desistiu da partida.' % argumento)
    elif int(num) == 2:
        print('Aceita jogar com o %s?' % argumento)
    elif int(num) == 3:
        print('%s rejeitou a partida!' % argumento)
    elif int(num) == 4:
        print('%s saiu!' % argumento)
    elif int(num) == 5:
        print('%s aceitou a partida! Você é o O' % argumento)
    else:
        print('Servidor enviou uma resposta desconhecida')


def cliente():
    if len(argv) < 4:
        raise RuntimeError('Falta argumentos!')
    conexão = Conexão(argv[1], argv[2], int(argv[3]))
    Thread(target=prompt_servidor, args=(conexão,)).start()
    while estado == 'rodando':
        comando, separador, argumento = conexão.recebe().partition(' ')
        if comando == 'resposta':
            interpreta_resposta(argumento)
        elif comando == 'ping':
            conexão.envia('pong %s' % argumento)
        elif comando == 'respostaLista':
            argumento.split(' ')
            print(*argumento.split(), sep='\n')
        elif comando == 'resposta_argumento':
            interpreta_resposta_argumento(argumento)
if __name__ == '__main__':
    cliente()
