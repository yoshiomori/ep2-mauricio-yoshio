from sys import argv
from biblioteca_cliente import Conexao, Deslogado, Logado


if len(argv) < 4:
    raise RuntimeError('Falta argumentos!')

conexao = Conexao(argv[1], argv[2], int(argv[3]))
deslogado = Deslogado(conexao)
logado = Logado(conexao)
estado = 'deslogado'
while estado is not 'morto':
    if estado is 'deslogado':
        estado = deslogado.cmdloop()
    elif estado is 'logado':
        estado = logado.cmdloop()
