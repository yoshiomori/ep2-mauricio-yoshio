from sys import exit
#Cria uma matriz do jogo da velha, por default os espacos
#sao preenchidos com +
def novaTela(tam=9):
    screen=[]    
    for i in range(0,tam):
        screen.append('+')    
    return screen

def inserir(tela):
    resultado=0
    valor="x" #default
    while valor!="+":
        m=int(raw_input("Digite o indice m: "))
        n=int(raw_input("Digite o indice n: "))
           
        valor=raw_input("Digite o valor: ")
        while valor!="x" and valor!="o":
            print "Valor invalido!"
            valor=raw_input("Digite o valor: ")
        
        if m==1:
            if n==1:
                tela[0]=valor
            elif n==2:
                tela[1]=valor
            elif n==3:
                tela[2]=valor
        elif m==2:
            if n==1:
                tela[3]=valor
            elif n==2:
                tela[4]=valor
            elif n==3:
                tela[5]=valor
        elif m==3:
            if n==1:
                tela[6]=valor
            elif n==2:  
                tela[7]=valor
            elif n==3:
                tela[8]=valor
        
        resultado=andamentoJogo(tela, valor)
        print "Resultado: ", resultado    
	        
        print valor
        print tela[0], tela[1], tela[2]
        print tela[3], tela[4], tela[5]
        print tela[6], tela[7], tela[8]
        
        if resultado=="x" or resultado=="o":
            exit(0)
        
        

def verificaLinha1(tela, jogador):
	i=0
	contador=0
	while i < 3:
		if tela[i]==jogador:
			contador+=1
		i+=1
	return contador

def verificaLinha2(tela, jogador):
	i=3
	contador=0
	while i>=3 and i <6:
		if tela[i]==jogador:
			contador+=1
		i+=1
	return contador

def verificaLinha3(tela, jogador):
	i=6
	contador=0
	while i>=6 and i<9:
		if tela[i]==jogador:
			contador+=1
		i+=1
	return contador


def verificaColuna1(tela, jogador):
	i=0
	contador=0
	while i<9:
		if tela[i]==jogador:
			contador+=1
		i+=3
	return contador

def verificaColuna2(tela, jogador):
	i=1
	contador=0
	while i<9:
		if tela[i]==jogador:
			contador+=1
		i+=3
	return contador

def verificaColuna3(tela, jogador):
	i=2
	contador=0
	while i<3:
		if tela[i]==jogador:
			contador+=1
		i+=3
	return contador

def verificaDiagPrincipal(tela, jogador):
	i=0	
	contador=0
	while i<9:
		if tela[i]==jogador:
			contador+=1
		i+=4
	return contador

def verificaDiagSecundaria(tela, jogador):
	i=6	
	contador=0
	while i>0:
		if tela[i]==jogador:
			contador+=1
		i-=2
	return contador
	

def andamentoJogo(tela, jogador):
	cont1=verificaLinha1(tela, jogador)
	cont2=verificaLinha2(tela, jogador)
	cont3=verificaLinha3(tela, jogador)
	cont4=verificaColuna1(tela, jogador)
	cont5=verificaColuna2(tela, jogador)
	cont6=verificaColuna3(tela, jogador)
	cont7=verificaDiagPrincipal(tela, jogador)
	cont8=verificaDiagSecundaria(tela, jogador)
	#Retorna o jogador que venceu 'X' ou 'O'
	if cont1==3 or cont2==3 or cont3==3 or cont4==3 or cont5==3 or cont6==3 or cont7==3 or cont8==3:
		print "O jogador: ", jogador, " eh o vencedor"
		return jogador	
	#Caso ninguem tenha vencido
	else:
		print "Jogo nao acabou"
		return 0
	
tela=novaTela()
tela=inserir(tela)
