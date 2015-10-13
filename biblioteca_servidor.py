from socket import socket, SOCK_DGRAM
from threading import Thread, Semaphore


class GerenciadorConexão(object):
    def __init__(self, tipo, porta):
        if tipo == 'tcp':
            s = socket()
            s.bind(('', porta))
            s.listen(1)

            def aceita():
                conexão_socket, endereco = s.accept()
                conexão = object()

                def recebe():
                    mensagem = conexão_socket.recv(1024)
                    return mensagem.decode()
                conexão.recebe = recebe

                def envia(mensagem):
                    conexão_socket.send(mensagem.encode('unicode_escape'))
                conexão.envia = envia
                return conexão
            self.aceita = aceita
        elif tipo == 'udp':
            s = socket(type=SOCK_DGRAM)
            s.bind(('', porta))

            endereços = []  # Guarda todos os endereços dos clientes que acessaram o servidor
            dados_clientes = []  # Guarda todas as pilhas de dados_clientes enviados pelos clientes
            tem_dados = []  # Guarda todos os semáforos que indicam se há dados_clientes na pilha.
            dados_lidos = []  # Guarda a infomação que o dado foi lido para cada conexão
            ultima_conexão = []  # Guarda a ultima conexão aceita
            semaforo_escuta_foi_consumido = Semaphore()
            semaforo_escuta_tem_produto = Semaphore()

            def gerenciador():
                while True:
                    dado, endereço = s.recvfrom(1024)  # O gerenciador fica esperando novas conexões
                    if endereço not in endereços:  # Trata mensagens provenientes de novos endereços
                        endereços.append(endereço)
                        dados_clientes.append(dado.decode())
                        tem_dado = Semaphore()
                        tem_dados.append(tem_dado)
                        dado_lido = Semaphore()
                        dados_lidos.append(dado_lido)
                        i = len(dados_clientes) - 1
                        conexao = object()  # criando uma nova conexão

                        def recebe():  # Uma conexão tem esse método que recebe informações vindas do cliente.
                            tem_dado.acquire()  # Uma conexão espera até ter um novo dado a ser lido
                            d = dados_clientes[i]
                            dado_lido.release()  # Uma conexão informa que o dado foi lido para o gerencidor
                            return d
                        conexao.recebe = recebe

                        def envia(mensagem):
                            s.sendto(mensagem.encode('unicode_escape'), endereço)
                        conexao.envia = envia
                        semaforo_escuta_foi_consumido.acquire()  # Fica esperando até a nova conexão ter sido processada
                        ultima_conexão.append(conexao)
                        semaforo_escuta_tem_produto.release()  # Indica que tem uma nova conexão para ser processada
                    else:
                        i = endereços.index(endereço)
                        dados_lidos[i].acquire()  # O gerencidor fica esperando até o dado ter sido lido pela conexão
                        dados_clientes[i].append(dado)
                        tem_dados[i].release()  # Informa que há um novo dado para ser lido
            Thread(target=gerenciador).start()

            def aceita():
                semaforo_escuta_tem_produto.acquire()  # Fica esperando até aparecer uma nova conexão a ser processada
                conexão = ultima_conexão.pop()
                semaforo_escuta_foi_consumido.release()  # Informa que a conexão foi processada
                return conexão
            self.aceita = aceita
            pass
        else:
            raise RuntimeError('Tipo de conexão não suportado.')
