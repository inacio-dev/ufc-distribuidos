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
GRPC_SERVER_PORT = 50052

# Intervalo para ligar/desligar o aquecedor (em segundos)
INTERVALO_LIGAR_DESLIGAR = 3

def conectar_atuador_grpc():
    channel = grpc.insecure_channel(f'{GRPC_SERVER_HOST}:{GRPC_SERVER_PORT}')
    return atuador_pb2_grpc.AtuadorStub(channel)

def enviar_comando_grpc(stub, comando, nome_atuador):
    try:
        if comando == "ligar":
            response = stub.LigarAquecedor(atuador_pb2.Solicitacao())
        elif comando == "desligar":
            response = stub.DesligarAquecedor(atuador_pb2.Solicitacao())
        else:
            print(f"Comando desconhecido: {comando}")
            return

        print(f"Comando enviado para {nome_atuador}: {response.status}")

    except grpc.RpcError as e:
        print(f"Erro ao se comunicar com o atuador {nome_atuador} via gRPC: {e}")
        status_code = e.code()
        details = e.details()
        print(f"Status Code: {status_code}, Details: {details}")


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
    # Lógica para processar os dados recebidos
    # Utilize os dicionários ou estruturas adequadas para armazenar e processar os dados conforme necessário
    print(f"Processando dados do sensor {sensor_nome}: {dados}")

    # Aqui você deve enviar os dados para o servidor TCP
    enviar_dados_tcp(sensor_nome, dados, tcp_socket)

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

    # Conectar ao atuador (aquecedor) via gRPC
    stub_atuador = conectar_atuador_grpc()

    # Exemplo de uso com threads para ligar/desligar o aquecedor
    thread_ligar_desligar = threading.Thread(target=ligar_desligar_aquecedor, args=(stub_atuador,))
    thread_ligar_desligar.start()

    # Aguardar as threads finalizarem
    thread_sensores.join()
    thread_ligar_desligar.join()

# Chamar a função para executar o HomeAssistant
executar_home_assistant()
