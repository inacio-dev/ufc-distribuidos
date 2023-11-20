import atuador_pb2
import atuador_pb2_grpc
import json
import time
import threading
import pika
import grpc
import socket

# Configurações do servidor TCP do HomeAssistant
TCP_SERVER_HOST = 'localhost'
TCP_SERVER_PORT = 5000

# Configurações do servidor gRPC dos atuadores
GRPC_SERVER_HOST = 'localhost'
AQUECEDOR_PORT = 50051
CONTROLE_INCENDIO_PORT = 50052
LAMPADA_PORT = 50053

# Intervalo para ligar/desligar o aquecedor (em segundos)
INTERVALO_LIGAR_DESLIGAR = 1

def conectar_atuador_grpc():
    channel = grpc.insecure_channel(f'{GRPC_SERVER_HOST}:{GRPC_SERVER_PORT}')
    return atuador_pb2_grpc.AtuadorStub(channel)

def enviar_comando_grpc(stub, comando, nome_atuador):
    try:
        # Obtém o método apropriado dinamicamente
        metodo_atuador = getattr(stub, f'{comando}{nome_atuador}')
        
        # Chama o método
        response = metodo_atuador(atuador_pb2.Solicitacao())

        print(f"Comando enviado para {nome_atuador}: {response.status}")

    except grpc.RpcError as e:
        print(f"Erro ao se comunicar com o atuador {nome_atuador} via gRPC: {e}")
        status_code = e.code()
        details = e.details()
        print(f"Status Code: {status_code}, Details: {details}")

# Função para ligar/desligar o atuador de aquecedor
def ligar_desligar_aquecedor(stub):
    while True:
        # Enviar comando para ligar
        enviar_comando_grpc(stub, "ligar", "Aquecedor")

        # Aguardar o intervalo
        time.sleep(INTERVALO_LIGAR_DESLIGAR)

        # Enviar comando para desligar
        enviar_comando_grpc(stub, "desligar", "Aquecedor")

        # Aguardar o intervalo
        time.sleep(INTERVALO_LIGAR_DESLIGAR)

# Função para ligar/desligar o atuador de lampada
def ligar_desligar_lampada(stub):
    while True:
        # Enviar comando para ligar o atuador de lampada
        enviar_comando_grpc(stub, "ligar", "Lampada")

        # Aguardar o intervalo
        time.sleep(INTERVALO_LIGAR_DESLIGAR)

        # Enviar comando para desligar o atuador de lampada
        enviar_comando_grpc(stub, "desligar", "Lampada")

        # Aguardar o intervalo
        time.sleep(INTERVALO_LIGAR_DESLIGAR)

# Função para ligar/desligar o atuador de controle de incendio
def ligar_desligar_controle_incendio(stub):
    while True:
        # Enviar comando para ligar o atuador de controle de incendio
        enviar_comando_grpc(stub, "ligar", "ControleIncendio")

        # Aguardar o intervalo
        time.sleep(INTERVALO_LIGAR_DESLIGAR)

        # Enviar comando para desligar o atuador de controle de incendio
        enviar_comando_grpc(stub, "desligar", "ControleIncendio")

        # Aguardar o intervalo
        time.sleep(INTERVALO_LIGAR_DESLIGAR)

def inicializar_filas_rabbitmq():
    while True:
        try:
            conexao = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            canal_sensores = conexao.channel()
            canal_sensores.queue_declare(queue='fila_sensores')
            return canal_sensores
        except pika.exceptions.AMQPError as e:
            print(f"Erro ao conectar ao RabbitMQ. Tentando novamente em 5 segundos... ({e})")
            time.sleep(5)

def criar_socket_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_SERVER_HOST, TCP_SERVER_PORT))
    return tcp_socket

def receber_dados_sensores(canal, tcp_socket):
    try:
        for method_frame, properties, body in canal.consume('fila_sensores'):
            if body and body.strip():
                try:
                    dados = json.loads(body.decode('utf-8'))
                    print(f"Recebido {dados['nome']}: {dados['dados']}")
                    # Chame a função para processar os dados
                    processar_dados_sensores(dados['nome'], dados['dados'], tcp_socket)
                except json.decoder.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
            else:
                print("Corpo da mensagem vazio ou composto apenas por espaços em branco.")
    except pika.exceptions.AMQPError as e:
        print(f"Erro ao receber dados dos sensores: {e}")
        # Lógica para reconectar ao RabbitMQ ou lidar com a desconexão

def processar_dados_sensores(sensor_nome, dados, tcp_socket):
    # Aqui você deve enviar os dados para o servidor TCP
    enviar_dados_tcp(sensor_nome, dados, tcp_socket)

    #enviar_dados_tcp("CommandAquecedor", tcp_socket)
    #enviar_dados_tcp("CommandLampada", tcp_socket)
    #enviar_dados_tcp("CommandControleIncendio", tcp_socket)

def processar_mensagem(mensagem, stub_atuador):
    print(f"Mensagem recebida do servidor.js: {mensagem}")

    # Lógica para processar a mensagem conforme necessário
    # Por exemplo, você pode enviar comandos para os atuadores gRPC aqui
    atuador = mensagem['atuador']
    dados_atuador = mensagem['dados']

    # Verificar qual atuador é mencionado na mensagem
    if atuador == 'CommandAquecedor':
        # Lógica específica para o atuador de aquecedor
        if dados_atuador['command'] == 'ligar':
            enviar_comando_grpc(stub_atuador, 'Ligar', 'Aquecedor')
        elif dados_atuador['command'] == 'desligar':
            enviar_comando_grpc(stub_atuador, 'Desligar', 'Aquecedor')
    elif atuador == 'CommandLampada':
        # Lógica específica para o atuador de lâmpada
        if dados_atuador['command'] == 'ligar':
            enviar_comando_grpc(stub_atuador, 'Ligar', 'Lampada')
        elif dados_atuador['command'] == 'desligar':
            enviar_comando_grpc(stub_atuador, 'Desligar', 'Lampada')
    elif atuador == 'CommandControleIncendio':
        # Lógica específica para o atuador de controle de incêndio
        if dados_atuador['command'] == 'ligar':
            enviar_comando_grpc(stub_atuador, 'Ligar', 'ControleIncendio')
        elif dados_atuador['command'] == 'desligar':
            enviar_comando_grpc(stub_atuador, 'Desligar', 'ControleIncendio')


def receber_dados_tcp(tcp_socket, stub_atuador):
    while True:
        try:
            # Aguardar a chegada de dados
            data = tcp_socket.recv(1024)

            if data:
                # Decodificar os dados recebidos
                mensagem = json.loads(data.decode('utf-8'))

                # Processar os dados conforme necessário
                processar_mensagem(mensagem, stub_atuador)
            else:
                print("Conexão fechada pelo servidor.")
                break  # Sair do loop quando a conexão for fechada
        except Exception as e:
            print(f"Erro ao receber dados do servidor TCP: {e}")

def enviar_dados_tcp(sensor_nome, dados, tcp_socket):
    try:
        # Preparar os dados a serem enviados
        dados_enviar = {'sensor': sensor_nome, 'dados': dados}

        # Enviar os dados para o servidor TCP
        tcp_socket.sendall(json.dumps(dados_enviar).encode('utf-8'))
        print(f"Dados enviados para o servidor TCP: {dados_enviar}")

    except Exception as e:
        print(f"Erro ao se comunicar com o servidor TCP: {e}")

def executar_home_assistant():
    canal_sensores = inicializar_filas_rabbitmq()

    # Criar socket TCP para se comunicar com o servidor
    tcp_socket = criar_socket_tcp()

    # Exemplo de uso com threads
    thread_sensores = threading.Thread(target=receber_dados_sensores, args=(canal_sensores, tcp_socket))
    thread_sensores.start()

    # Inicializar a conexão gRPC para cada atuador
    stub_aquecedor = conectar_atuador_grpc(AQUECEDOR_PORT)
    stub_controle_incendio = conectar_atuador_grpc(CONTROLE_INCENDIO_PORT)
    stub_lampada = conectar_atuador_grpc(LAMPADA_PORT)

    # Iniciar a thread para receber mensagens TCP
    thread_aquecedor = threading.Thread(target=receber_dados_tcp, args=(tcp_socket, stub_aquecedor))
    thread_aquecedor.start()
    thread_controle_incendio = threading.Thread(target=receber_dados_tcp, args=(tcp_socket, stub_controle_incendio))
    thread_controle_incendio.start()
    thread_lampada = threading.Thread(target=receber_dados_tcp, args=(tcp_socket, stub_lampada))
    thread_lampada.start()

    # Aguardar a thread finalizar
    thread_tcp.join()

# Chamar a função para executar o HomeAssistant
executar_home_assistant()
