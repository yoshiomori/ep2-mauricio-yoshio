from sys import argv
from biblioteca_cliente import Conexao, Deslogado, Logado


if len(argv) < 4:
    raise RuntimeError('Falta argumentos!')

conexao = Conexao(argv[1], argv[2], int(argv[3]))
deslogado = Deslogado(conexao)
logado = Logado(conexao)
estado = 'deslogado'
while estado != 'morto':
    if estado == 'deslogado':
        estado = deslogado.rodando()
    elif estado == 'logado':
        estado = logado.rodando()
    else:
        raise RuntimeError('Estado desconhecido.')
