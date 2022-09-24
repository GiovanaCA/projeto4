#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2022
# Aplicação
####################################################

#       SERVER4

# esta é a camada superior, de aplicação do seu software de comunicação serial UART.

from http.cookiejar import LWPCookieJar
from enlace import *
import time
from datetime import datetime


#   python -m serial.tools.list_ports

# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/cu.usbmodem11101"  # Mac    (variacao de)
serialName = "COM8"                  # Windows(variacao de)

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)

        # Ativa comunicacao. Inicia os threads e a comunicação serial
        print("Abriu a comunicação")
         
        # HANDSHAKE RESPOSTA
        
        ocioso = True
        while ocioso:
            
            # RECEBENDO O HANDSHAKE
            conteudo = com1.rx.getIsEmpty()
            if conteudo == False:
                head, nRx = com1.getData(10)
                print(head)
                tamanho = head[5]
                numPckg = head[3]
                handshake, nRx = com1.getData(tamanho)
                EOP, nEop = com1.getData(4)
                arquivo = open('Server1.txt', 'a')
                arquivo.write("{} / receb / 1 / 14\n".format(datetime.now()))
                arquivo.close()   
                print("Handshake recebido")
                print(head)
                com1.rx.clearBuffer()
              
              	# É O HANDSHAKE MESMO
              
                if head[0] == 1:
                  
                  	# É PRA MIM MESMO
                  
                    if head[5] == 17:
                        time.sleep(.1)
                        ocioso = False
                    else:
                        time.sleep(.1)
            else:
                time.sleep(.1)
        eop = b'\xAA\xBB\xCC\xDD'
        hresposta = b'\x02\x00\x00' + bytes([numPckg]) +  b'\x00\x11\x00\x00\x00\x00' + eop
        com1.sendData(hresposta)
        arquivo = open('Server1.txt', 'a')
        arquivo.write("'{}' / envio / 2 / '{}' / '{}' / '{}'\n".format(datetime.now(), hresposta[5]+14, hresposta[4],hresposta[3]))
        arquivo.close()
        cont = 1
        print("Enviado resposta do handshake")
        time.sleep(.1)
        
        string = b''
        pacote_recebido_certo = b'\x01'
        nump = 0
        while cont <= numPckg:
            time.sleep(.1)
            print("reiniciou")
            timer1 = time.time()
            timer2 = time.time()
            n_sucesso = True
            while n_sucesso:
                agora = time.time()
                time.sleep(.1)
                conteudo = com1.rx.getIsEmpty()
                if conteudo == False: 
                    head, nPacote = com1.getData(10)
                    print(head)
                    numero = head[4]
                    tamanho = head[5]
                    tipo = head[0]
                    print(tipo)
                    #verifica se é do tipo 3
                    if tipo == 3:
                        x, nX = com1.getData(tamanho)
                        string += x
                        eop, nEop = com1.getData(4)
                        arquivo = open('Server1.txt', 'a')
                        arquivo.write("'{}' / receb / 3 / '{}'\n".format(datetime.now(), tamanho+14))
                        arquivo.close()   
                        #verifica se está na ordem
                        if numero == nump+1:
                            print("numero do pacote esperado certo")
                            # verifica se é do eop
                            if eop ==  b'\xAA\xBB\xCC\xDD':
                                print("eop certo")
                                cont +=1
                                nump = head[4]
                                com1.sendData(b'\x04\x00\x00\x00\x00\x00\x00' + pacote_recebido_certo + b'\x00\x00\xAA\xBB\xCC\xDD')
                                arquivo = open('Server1.txt', 'a')
                                arquivo.write("'{}' / envio / 4 / '{}' / '{}' / '{}'\n".format(datetime.now(), hresposta[5]+14, hresposta[4],hresposta[3]))
                                arquivo.close()
                                pacote_recebido_certo = bytes([numero])
                            else:
                                print("eop errado")
                                pacote_recebido_errado = nump + 1
                                com1.sendData(b'\x06\x00\x00\x00\x00\x00' + bytes([pacote_recebido_errado]) + b'\x00\x00\x00\xAA\xBB\xCC\xDD')
                                arquivo = open('Server2.txt', 'a')
                                arquivo.write("'{}' / envio / 6 / '{}' / '{}' / '{}'\n".format(datetime.now(), hresposta[5]+14, hresposta[4],hresposta[3]))
                                arquivo.close()
                        else:
                            pacote_recebido_errado = nump + 1
                            print("numero do pacote esperado errado")
                            com1.sendData(b'\x06\x00\x00\x00\x00\x00' + bytes([pacote_recebido_errado]) + b'\x00\x00\x00\xAA\xBB\xCC\xDD')
                            arquivo = open('Server1.txt', 'a')
                            arquivo.write("'{}' / envio / 6 / '{}' / '{}' / '{}'\n".format(datetime.now(), hresposta[5]+14, hresposta[4],hresposta[3]))
                            arquivo.close()
                elif agora-timer2 > 20:
                    com1.sendData(b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\xAA\xBB\xCC\xDD')
                    arquivo = open('Server1.txt', 'a')
                    arquivo.write("'{}' / envio / 5 / '{}' / '{}' / '{}'\n".format(datetime.now(), hresposta[5]+14, hresposta[4],hresposta[3]))
                    arquivo.close()
                    print("Time out")
                    print("Encerra")
                    com1.disable()
                    print("-------------------------")
                    print("Comunicação encerrada")
                    print("-------------------------")
                    break
                elif agora-timer1 > 2:
                        com1.sendData(b'\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xAA\xBB\xCC\xDD')
                        arquivo = open('Server1.txt', 'a')
                        arquivo.write("'{}' / envio / 4 / '{}' / '{}' / '{}'\n".format(datetime.now(), hresposta[5]+14, hresposta[4],hresposta[3]))
                        arquivo.close()
                        timer1 = time.time()

        print("chegou")
        imageW = 'crawfinal.png'

        f = open(imageW, 'wb')
        f.write(string)
        f.close()
        
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

    # so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda


if __name__ == "__main__":
    main()