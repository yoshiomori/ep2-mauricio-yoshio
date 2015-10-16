from threading import Thread, Semaphore
from biblioteca_servidor import GerenciadorTCP, GerenciadorUDP
from time import sleep, localtime, ctime


usuários = ['velha', 'dr3m', 'maisum']  # nickname é um identificador
senhas = ['123', 'daf', '25jan90']
estados = ['deslogado', 'deslogado', 'deslogado']
conexões = [None, None, None]
jogos = {}
jogo_id = 0
usando_jogo_id = Semaphore()
pontos = [0, 0, 0]
numero_ping = 0
pings = {}
no_ping = Semaphore()

lt = localtime()


def chegou_ping(argumento):
    no_ping.acquire()
    pings[int(argumento)] = True
    no_ping.release()


def interpreta_deslogado(mensagem):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'deslogado'
    mensagem = 'resposta 14'
    i = -1
    if comando == 'login':
        if argumento in usuários:
            i = usuários.index(argumento)
            if estados[i] == 'logado' or estados[i] == 'jogando':
                mensagem = 'resposta 3'
            else:
                mensagem = 'resposta 4'
                próximo_estado = 'autenticando'
        else:
            mensagem = 'resposta 2'
    elif comando == 'cadastro':
        if argumento not in usuários:
            usuários.append(argumento)
            senhas.append('')
            estados.append('deslogado')
            conexões.append(None)
            i = usuários.index(argumento)
            mensagem = 'resposta 5'
            próximo_estado = 'cadastrando'
        pass
    elif comando == 'sair':
        mensagem = 'resposta 6'
        próximo_estado = 'fim'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
    return mensagem, próximo_estado, i


def interpreta_autenticando(mensagem, i, conn, j, jid):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'autenticando'
    mensagem = 'resposta 14'
    if comando == 'senha':
        if argumento == senhas[i]:
            if estados[i] != 'jogando e desconectado':
                mensagem = 'resposta 7'
                estados[i] = próximo_estado = 'logado'
            else:
                mensagem = 'resposta 15'
                estados[i] = próximo_estado = 'jogando'
                for k in jogos.keys():
                    if i in jogos[k]:
                        jid = k
                        j = jogos[k][1] if jogos[k][1] != i else jogos[k][2]
                        conexões[j].envia('resposta_argumento 6 %s' % usuários[i])
                        conexões[j].envia('voltei')
            conexões[i] = conn
        else:
            mensagem = 'resposta 16'
    elif comando == 'sair':
        mensagem = 'resposta 6'
        próximo_estado = 'fim'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
        pass
    return mensagem, próximo_estado, j, jid


def interpreta_cadastrando(mensagem, i):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'cadastrando'
    mensagem = 'resposta 14'
    if comando == 'senha':
        senhas[i] = argumento
        pass
    elif comando == 'sair':
        mensagem = 'resposta 6'
        usuários.pop(i)
        senhas.pop(i)
        estados.pop(i)
        conexões.pop(i)
        próximo_estado = 'fim'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 1'
        pass
    return mensagem, próximo_estado


def interpreta_logado(mensagem, i, j):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'logado'
    mensagem = 'resposta 14'
    if comando == 'listar':
        mensagem = 'respostaLista '
        mensagem += 'usuario-estado '
        for j, usuário in enumerate(usuários):
            mensagem += "%s-%s " % (usuário, estados[j]) if j != i else ''
        pass
    elif comando == 'jogar':
        if argumento in usuários:
            j = usuários.index(argumento)
            if j != i and estados[j] == 'logado':
                mensagem = 'resposta 8'
                próximo_estado = estados[i] = 'aguardando jogador'
                conexões[j].envia('resposta_argumento 2 %s' % usuários[i])
                conexões[j].envia('convite %d' % i)  # Para convidar é preciso apresentar sua identificação
            else:
                mensagem = 'resposta 2'
        else:
            mensagem = 'resposta 2'
        pass
    elif comando == 'convite':
        mensagem = 'resposta 14'
        próximo_estado = estados[i] = 'aguardando resposta'
        j = int(argumento)
    elif comando == 'fame':
        fame = list(zip(pontos, usuários))
        fame.sort(key=lambda x: x[0])
        mensagem = 'respostaLista '
        for ponto, usuário in fame:
            mensagem += "%s-%d " % (usuário, ponto)
        pass
    elif comando == 'sair':
        mensagem = 'resposta 6'
        próximo_estado = 'fim'
        estados[i] = 'deslogado'
        conexões[i] = None
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
        pass
    return mensagem, próximo_estado, j


def interpreta_jogando(mensagem, i, j, jid):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'jogando'
    mensagem = 'resposta 14'
    if comando == 'mostre':
        pass
    elif comando == 'marcar':
        pass
    elif comando == 'sair':
        mensagem = 'resposta 12'
        estados[i] = 'logado'
        próximo_estado = 'logado'
        conexões[j].envia('respota_argumento 1 %s' % usuários[i])
        conexões[j].envia('jogo_cancelado')
    elif comando == 'cancelar':
        mensagem = 'resposta 13'
        estados[i] = 'logado'
        próximo_estado = 'logado'
        # TODO: marcar pontuação antes de destruir o jogo
        jogos.pop(jid)
    elif comando == 'espera_voltar':
        próximo_estado = 'espera voltar'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
        pass
    return mensagem, próximo_estado


def interpreta_aguardando_jogador(mensagem, i, j, jid):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'aguardando jogador'
    mensagem = 'resposta 14'
    if comando == 'listar':
        mensagem = 'respostaLista '
        for j, usuário in enumerate(usuários):
            mensagem += "%s " % usuário if j != i else ''
        pass
    elif comando == 'fame':
        fame = list(zip(pontos, usuários))
        fame.sort(key=lambda x: x[0])
        mensagem = 'respostaLista '
        for ponto, usuário in fame:
            mensagem += "%s-%d " % (usuário, ponto)
        pass
    elif comando == 'jogo_aceito':
        mensagem = 'resposta 14'
        próximo_estado = estados[i] = 'jogando'
        jid = int(argumento)
    elif comando == 'sair':
        mensagem = 'resposta 12'
        estados[i] = 'logado'
        próximo_estado = 'logado'
        conexões[j].envia('respota_argumento 1 %s' % usuários[i])
        conexões[j].envia('jogo_cancelado')
    elif comando == 'cancelar':
        mensagem = 'resposta 13'
        estados[i] = 'logado'
        próximo_estado = 'logado'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
        pass
    return mensagem, próximo_estado, jid


def interpreta_aguardando_resposta(mensagem, i, j, jid):
    global jogo_id
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'aguardando resposta'
    mensagem = 'resposta 14'
    if comando == 'sim':
        mensagem = 'resposta 9'
        estados[i] = próximo_estado = 'jogando'
        usando_jogo_id.acquire()
        jid = jogo_id
        jogo_id += 1
        usando_jogo_id.release()
        # TODO: Instanciando um jogo no None
        jogos[jogo_id] = [None, i, j]
        conexões[j].envia('resposta_argumento 4 %s' % usuários[i])
        conexões[j].envia('jogo_aceito %d' % jid)  # O jogo é criado pelo convidado e é enviado para o outro jogado
    elif comando == 'não':
        mensagem = 'resposta 10'
        estados[i] = próximo_estado = 'logado'
        conexões[j].envia('resposta_argumento 3 %s' % usuários[i])
        conexões[j].envia('jogo_cancelado')
    elif comando == 'cancelar':
        mensagem = 'resposta 13'
        estados[i] = 'logado'
        próximo_estado = 'logado'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
        pass
    return mensagem, próximo_estado, jid


def interpreta_espera_voltar(mensagem, i, j, jid):
    comando, sep, argumento = mensagem.partition(' ')
    próximo_estado = 'espera voltar'
    mensagem = 'resposta 14'
    if comando == 'cancelar':
        mensagem = 'resposta 13'
        próximo_estado = estados[i] = 'logado'
        if estados[i] == 'jogando':  # Destruindo jogo
            # TODO: marcar pontuação antes de destruir o jogo
            jogos.pop(jid)
        estados[j] = 'deslogado'
    elif comando == 'voltei':
        mensagem = 'resposta 15'
        próximo_estado = estados[i] = 'jogando'
    elif comando == 'pong':
        chegou_ping(argumento)
    else:
        mensagem = 'resposta 0'
    return mensagem, próximo_estado, jid


def serviço(conn):  # Essa função roda para cada novo cliente conectado
    global conexões, numero_ping, pings, estados
    log = open('%d-%d-%d.log' % (lt.tm_year, lt.tm_mon, lt.tm_mday), 'a', newline='\n')
    log.write('[{}]Cliente {} conectou!\n'.format(ctime(), conn.endereço))
    conn.envia('resposta 11')
    estado = 'deslogado'
    j = -1
    i = -1
    jid = -1

    def heartbeat():
        nonlocal estado, j
        global pings, numero_ping
        no_ping.acquire()
        meu_ping = numero_ping
        numero_ping += 1
        no_ping.release()
        while estado != 'fim':
            no_ping.acquire()
            conn.envia('ping %d' % meu_ping)
            pings[meu_ping] = False
            no_ping.release()
            sleep(5)
            if not pings[meu_ping]:
                if estado == 'logado':
                    estados[i] = 'deslogado'
                    log.write('[{}]Cliente {}, logado como {}, perdeu a conexão\n'.format(ctime(), conn.endereço,
                                                                                          usuários[i]))
                elif estado == 'jogando':
                    conexões[j].envia('resposta_argumento 5 %s' % usuários[i])
                    conexões[j].envia('espera_voltar')
                    estados[i] = 'jogando e desconectado'
                    log.write('[{}]Cliente {}, logado como {}, perdeu a conexão e estava jogando com {}\n'.format(
                        ctime(), conn.endereço, usuários[i], usuários[j]))
                elif estado == 'cadastrando':
                    usuários.pop(i)
                    senhas.pop(i)
                    estados.pop(i)
                    conexões.pop(i)
                    log.write('[{}]Cliente {} perdeu a conexão e não consegui cadastrar {}\n'.format(ctime(),
                                                                                                     conn.endereço,
                                                                                                     usuários[i]))
                elif estado == 'aguardando jogador':
                    conexões[i] = None
                    conexões[j].envia('respota_argumento 0 %s' % usuários[i])
                    estados[i] = 'deslogado'
                    conexões[j].envia('jogo_cancelado')
                    log.write('[{}]Cliente {}, logado como {}, perdeu a conexão e o jogo com {} foi cancelado\n'.format(
                        ctime(), conn.endereço, usuários[i], usuários[j]))
                elif estado == 'aguardando resposta':
                    estados[i] = 'deslogado'
                    conexões[i] = None
                    conexões[j].envia('respota_argumento 0 %s' % usuários[i])
                    conexões[j].envia('jogo_cancelado')
                    log.write('[{}]Cliente {}, logado como {}, perdeu a conexão e o jogo com {} foi cancelado\n'.format(
                        ctime(), conn.endereço, usuários[i], usuários[j]))
                estado = 'fim'
        pings.pop(meu_ping)

    def interpreta_cliente():
        nonlocal estado, conn, i, j, jid
        while estado != 'fim':  # estado guarda o estado atual do serviço
            mensagem = conn.recebe()
            if estado == 'deslogado':
                log.write('[{}]Cliente {} enviou {}\n'.format(ctime(), conn.endereço, mensagem))
                mensagem, estado, i = interpreta_deslogado(mensagem)
            elif estado == 'autenticando':
                mensagem, estado, j, jid = interpreta_autenticando(mensagem, i, conn, j, jid)
            elif estado == 'cadastrando':
                mensagem, estado = interpreta_cadastrando(mensagem, i)
            elif estado == 'logado':
                log.write('[{}]Cliente {}, logado como {}, enviou {}\n'.format(ctime(), conn.endereço, usuários[i],
                                                                               mensagem))
                mensagem, estado, j = interpreta_logado(mensagem, i, j)
            elif estado == 'jogando':
                log.write('[{}]Cliente {}, logado como {} e em jogo com {}, enviou {}\n'.format(ctime(), conn.endereço,
                                                                                                usuários[i],
                                                                                                usuários[j], mensagem))
                mensagem, estado = interpreta_jogando(mensagem, i, j, jid)
            elif estado == 'aguardando jogador':
                log.write('[{}]Cliente {}, logado como {}, enviou {} e está aguardando {}\n'.format(ctime(),
                                                                                                    conn.endereço,
                                                                                                    usuários[i],
                                                                                                    mensagem,
                                                                                                    usuários[j]))
                mensagem, estado, jid = interpreta_aguardando_jogador(mensagem, i, j, jid)
            elif estado == 'aguardando resposta':
                log.write('[{}]Cliente {}, logado como {}, enviou {} e deve responder ao {}\n'.format(ctime(),
                                                                                                      conn.endereço,
                                                                                                      usuários[i],
                                                                                                      mensagem,
                                                                                                      usuários[j]))
                mensagem, estado, jid = interpreta_aguardando_resposta(mensagem, i, j, jid)
            elif estado == 'espera voltar':
                log.write('[{}]Cliente {}, logado como {}, enviou {} e deve responder se espera o jogador {}'
                          ' reestabelecer conexão\n'.format(ctime(), conn.endereço, usuários[i], mensagem, usuários[j]))
                mensagem, estado, jid = interpreta_espera_voltar(mensagem, i, j, jid)
            else:
                raise RuntimeError('Serviço entrou em um estado disconhecido.')
            conn.envia(mensagem)
    Thread(target=interpreta_cliente).start()
    theartbeat = Thread(target=heartbeat)
    theartbeat.start()
    theartbeat.join()
    log.write('[{}]Cliente {} desconectou!\n'.format(ctime(), conn.endereço))
    log.close()
    conn.encerra()


def servidor(gerenciador):
    while True:  # Servidor udp não precisa de threads pois lida da mesma forma cada pacote
        conn = gerenciador.aceita()
        Thread(target=serviço, args=(conn,)).start()  # Cada conexão estabelecida gera uma thread
Thread(target=servidor, args=(GerenciadorTCP(50007),)).start()  # Iniciando servidor tcp
servidor(GerenciadorUDP(50007))  # Iniciando servidor udp
