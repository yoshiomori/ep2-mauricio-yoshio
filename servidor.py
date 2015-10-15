from threading import Thread
from biblioteca_servidor import GerenciadorTCP, GerenciadorUDP


usuários = ['velha', 'dr3m', 'maisum']  # nickname é um identificador
senhas = ['123', 'daf', '25jan90']
estados = ['deslogado', 'deslogado', 'deslogado']
conexões = [None, None, None]
pontos = [0, 0, 0]


def interpreta_deslogado(mensagem):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'deslogado'
    i = -1
    if comando == 'login':
        if argumento in usuários:
            i = usuários.index(argumento)
            if estados[i] == 'logado' or estados[i] == 'jogando':
                mensagem = 'Usuário em uso!'
            else:
                mensagem = 'Aguardando senha'
                próximo_estado = 'autenticando'
        else:
            mensagem = 'Usuário inválido!'
    elif comando == 'cadastro':
        if argumento not in usuários:
            usuários.append(argumento)
            senhas.append('')
            estados.append('deslogado')
            conexões.append(None)
            i = usuários.index(argumento)
            mensagem = 'Nome de usuário cadastrado'
            próximo_estado = 'cadastrando'
        pass
    elif comando == 'sair':
        mensagem = 'sair'
        próximo_estado = 'fim'
        pass
    elif comando == 'ping':
        mensagem = 'pong'
        pass
    else:
        mensagem = 'Comando não é válido'
    return mensagem, próximo_estado, i


def interpreta_autenticando(mensagem, i):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'autenticando'
    if comando == 'senha':
        if argumento == senhas[i]:
            mensagem = 'Logado'
            próximo_estado = 'logado' if estados[i] != 'jogando e desconectado' else 'jogando'
    elif comando == 'sair':
        mensagem = 'saindo'
        próximo_estado = 'fim'
        pass
    elif comando == 'ping':
        mensagem = 'pong'
        pass
    else:
        mensagem = 'comando inválido! aguardando senha'
        pass
    return mensagem, próximo_estado


def interpreta_cadastrando(mensagem, i):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'cadastrando'
    if comando == 'senha':
        senhas[i] = argumento
        pass
    elif comando == 'sair':
        mensagem = 'saindo'
        usuários.pop(i)
        senhas.pop(i)
        estados.pop(i)
        conexões.pop(i)
        próximo_estado = 'deslogado'
        pass
    elif comando == 'ping':
        mensagem = 'pong'
        pass
    else:
        mensagem = 'Comando não é válido. Aguardando senha!'
        pass
    return mensagem, próximo_estado


def interpreta_logado(mensagem, i):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'logado'
    if comando == 'listar':
        mensagem = ''
        for j, usuário in enumerate(usuários):
            mensagem += "%s\n" % usuário if j != i else ''
        pass
    elif comando == 'jogar':
        if argumento in usuários:
            j = usuários.index(argumento)
            if j != i and estados[j] == 'logado':
                mensagem = 'Convidando'
                conexões[j].envia('Aceita jogar com o %s?' % usuários[i])
                próximo_estado = estados[i] = 'Aguardando jogador'
                estados[j] = 'Aguardando resposta'
            else:
                mensagem = 'Usuário inválido'
        pass
    elif comando == 'fame':
        fame = list(zip(pontos, usuários))
        fame.sort(key=lambda x: x[0])
        mensagem = ''
        for ponto, usuário in fame:
            mensagem += "%s %d\n" % (usuário, ponto)
        pass
    elif comando == 'sair':
        mensagem = 'Saindo'
        próximo_estado = 'fim'
        estados[i] = 'deslogado'
        conexões[i] = None
        pass
    elif comando == 'ping':
        mensagem = 'pong'
        pass
    else:
        mensagem = 'Comando não é válido!'
        pass
    return mensagem, próximo_estado


def interpreta_jogando(mensagem, i):
    comando, sep, argumento = mensagem.partition(' ')
    if comando == 'mostre':
        pass
    elif comando == 'marcar':
        pass
    elif comando == 'mensagem':
        pass
    elif comando == 'sair':
        pass
    elif comando == 'ping':
        pass
    else:
        pass
    return mensagem, 'jogando'


def serviço(conn):  # Essa função roda para cada novo cliente conectado
    global conexões
    estado = 'deslogado'
    while estado != 'fim':  # estado guarda o estado atual do serviço
        mensagem = conn.recebe()
        if estado == 'deslogado':
            mensagem, estado, i = interpreta_deslogado(mensagem)
        elif estado == 'autenticando':
            mensagem, estado = interpreta_autenticando(mensagem, i)
        elif estado == 'cadastrando':
            mensagem, estado = interpreta_cadastrando(mensagem, i)
        elif estado == 'logado':
            conexões[i] = conn
            mensagem, estado = interpreta_logado(mensagem, i)
        elif estado == 'jogando':
            mensagem, estado = interpreta_jogando(mensagem, i)
        else:
            raise RuntimeError('Serviço entrou em um estado disconhecido.')
        conn.envia(mensagem)


def servidor(gerenciador):
    while True:  # Servidor udp não precisa de threads pois lida da mesma forma cada pacote
        conn = gerenciador.aceita()
        Thread(target=serviço, args=(conn,)).start()  # Cada conexão estabelecida gera uma thread
Thread(target=servidor, args=(GerenciadorTCP(50007),)).start()  # Iniciando servidor tcp
servidor(GerenciadorUDP(50007))  # Iniciando servidor udp
