from threading import Thread
from biblioteca_servidor import GerenciadorConexão


def server(gerenciador_conexão):
    def echo():  # Essa função roda para cada novo cliente conectado
        print(conn)
        data = conn.recebe()
        conn.envia(data)
        # conn.close()
    nicknames = ['velha', 'dr3m', 'maisum']  # nickname é um identificador
    senhas = ['123', 'daf', '25jan90']
    estados = ['deslogado', 'deslogado', 'deslogado']
    while True:  # Servidor udp não precisa de threads pois lida da mesma forma cada pacote
        conn = gerenciador_conexão.aceita()
        Thread(target=echo, args=(conn,)).start()  # Cada conexão estabelecida gera uma thread


Thread(target=server, args=(GerenciadorConexão('tcp', 50007),)).start()  # Iniciando servidor tcp
server(GerenciadorConexão('udp', 50007))  # Iniciando servidor udp
