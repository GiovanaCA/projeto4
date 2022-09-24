#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2022
# Aplicação
####################################################

#       CLIENT4

# esta é a camada superior, de aplicação do seu software de comunicação serial UART.

from enlace import *
import time
import numpy as np
import random
from datetime import datetime

#   python -m serial.tools.list_ports
# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "COM7" # Mac    (variacao de)
#serialName = "/dev/cu.usbmodem11101"  # Mac    (variacao de)

# estrutura de head:
# h0 – tipo de mensagem
# h1 – livre
# h2 – livre
# h3 – total de pacotes do arquivo (YES em todos)
# h4 – número do pacote sendo enviado (YES a partir do tipo 3)
# h5 – se tipo for handshake: id do arquivo (crie um)
# h5 – se tipo for dados: tamanho do payload
# h6 – pacote solicitado para recomeço quando a erro no envio.
# h7 – último pacote recebido com sucesso.
# h8 – h9 – CRC (Por ora deixe em branco. Fará parte do projeto 5)

# tipos do h0 :
# b'\x01' - handshake
# b'\x02' - hanshake resposta
# b'\x03' - dados
# b'\x04' - dados resposta
# b'\x05' - time out
# b'\x06' - erro

def main():
    try:
        print("Iniciou o main")

        erro2 = True
        com1 = enlace(serialName)
        com1.enable()
        time.sleep(.2)
        com1.sendData(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xAA\xBB\xCC\xDD')
        time.sleep(1)
        print("Abriu a comunicação")

        img = "img.png"

		# FORMANDO PAYLOAD
        pl = []
        image = open(img, 'rb').read()
        for n in range(len(image)):
            if n == 0:
                pass
            elif n % 114 == 0:
                cortar = image[n-114:n]
                pl.append(cortar)
        # Contar quantidade de bytes em payload
        contador = 0
        for i in pl:
            contador += len(i)
        cortar = image[contador:len(image)]
        pl.append(cortar)
        
        # FORMANDO HANDSHAKE
        eop = b'\xAA\xBB\xCC\xDD'
        numPck = len(pl)
        totalpacotes = bytes([numPck])
        h = b'\x01\x10\x00' + totalpacotes +  b'\x00\x11\x00\x00\x00\x00' + eop
        com1.sendData(np.asarray(h))
        print("Handshake enviado")
        arquivo = open('Client1.txt', 'a')
        arquivo.write("{} / envio / 1 / 14\n".format(datetime.now()))
        arquivo.close()
        time.sleep(.1)

        # Tempo
        while True:
            time.sleep(5)
            conteudo = com1.rx.getIsEmpty()
            if conteudo == False:
                h_resposta, n = com1.getData(10)
                EOP, n3 = com1.getData(4)
                print("O Handshake resposta foi recebido")
                break
            else:
                print("Entrou aqui pois o handshake resposta nao foi recebido antes de 5 seg")
                print("Tentando")
                time.sleep(.2)
                com1.sendData(b'0000000')
                time.sleep(1)
                print("Abriu a comunicação")
                com1.sendData(np.asarray(h))
                print("Handshake enviado")
                arquivo = open('Client1.txt', 'a')
                arquivo.write("{} / envio / 1 / 14\n".format(datetime.now()))
                arquivo.close()
                continue

        cont = 1
        while True:
            # FORMANDO LOGICA
            pacote_recebido_certo = b'\x00'
            while cont <= numPck:
                i = pl[cont-1]
                if i != '':
                    tam_payload = bytes([len(i)])
                    num_pacote = bytes([cont])
                    head = b'\x03'+ b'\x00\x00'+ totalpacotes + num_pacote + tam_payload + b'\x00' + pacote_recebido_certo + b'\x00\x00'    
                    pacote = head + i + eop
                    com1.sendData(np.asarray(pacote))
                    arquivo = open('Client1.txt', 'a')
                    arquivo.write("{} / envio / 3 / {} / {} / {}\n".format(datetime.now(), len(i)+14, cont, numPck))
                    arquivo.close()
                    print("Pacote {} enviado" .format(cont))
                    timer1 = time.time()
                    timer2 = time.time()
                    n_sucesso = True
                    while n_sucesso:
                        agora = time.time()
                        time.sleep(.1)
                        conteudo = com1.rx.getIsEmpty()
                        if conteudo == False: 
                            head, n = com1.getData(10)
                            time.sleep(.1)
                            print(head)
                            if head[0] != 4:
                                print(head)
                                s_head, n = com1.getData(10)
                                num2 = s_head[3]
                                num_pacote = s_head[4]
                                tam_payload = s_head[5]
                                pacote_a_enviar = s_head[6]
                                payload, n2 = com1.getData(num2)
                                eop, n3 = com1.getData(4)
                                arquivo = open('Client1.txt', 'a')
                                arquivo.write("{} / receb / {} / 14\n".format(datetime.now(), num2))
                                arquivo.close()
                                if s_head[0] != b'\x06':
                                    print("O pacote nao esta errado")
                                else:
                                    timer1 = time.time()
                                    timer2 = time.time()
                                    head = b'\x03'+ b'\x00\x00'+ totalpacotes + num_pacote + tam_payload + pacote_a_enviar + pacote_recebido_certo + b'\x00\x00'    
                                    pacote = head + i + eop
                                    com1.sendData(np.asarray(pacote))
                                    print("Pacote {} enviado" .format(cont))
                                    arquivo = open('Client1.txt', 'a')
                                    arquivo.write("{} / envio / 3 / {} / {} / {}\n".format(datetime.now(), len(i)+14, cont, numPck))
                                    arquivo.close()
                            else:
                                cont += 1
                                if cont == 5 and erro2:
                                    cont = 6
                                    erro2 = False
                                tamanho = head[5]
                                arquivo = open('Client1.txt', 'a')
                                arquivo.write("{} / receb / 4 / {}\n".format(datetime.now(), tamanho+14))
                                arquivo.close()  
                                payload, n = com1.getData(tamanho)
                                eop, n = com1.getData(4)
                                agora = time.time()
                                n_sucesso = False
                        elif (agora-timer1) > 5:
                            com1.sendData(np.asarray(pacote))
                            print("Reenviando pacote {}" .format(cont))
                            arquivo = open('Client1.txt', 'a')
                            arquivo.write("{} / envio / 3 / {} / {} / {}\n".format(datetime.now(), len(i)+14, cont, numPck))
                            arquivo.close()
                            timer1 = time.time()       
                        elif (agora-timer2) > 20:
                            print("Time out")
                            com1.sendData(b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\xAA\xBB\xCC\xDD')
                            arquivo = open('Client1.txt', 'a')
                            arquivo.write("{} / envio / 5 / 14\n".format(datetime.now()))
                            arquivo.close()
                            n_sucesso = False
                            cont = numPck + 1
                            print("Encerra")

                        else:
                            pass
                else:
                    cont += 1
            break

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

    # so roda o main quando for executado do terminal... se for chamado dentro de outro modulo nao roda
    
if __name__ == "__main__":
    main()