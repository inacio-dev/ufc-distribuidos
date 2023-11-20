import time
import random
import json
import pika

def enviar_dados(sensor_nome, canal):
    while True:
        presenca_fumaca = random.choice(['Sim', 'Não'])
        mensagem = {
            'nome': sensor_nome,  # Alterado para 'nome' para corresponder à estrutura esperada pelo HomeAssistant
            'dados': {
                'presenca_fumaca': presenca_fumaca,
                'timestamp': int(time.time())
            }
        }

        canal.basic_publish(
            exchange='',
            routing_key='fila_sensores',  # Alterado para 'fila_sensores' para corresponder à fila no HomeAssistant
            body=json.dumps(mensagem)
        )

        print(f"Enviado: {mensagem}")
        time.sleep(5)

conexao = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
canal = conexao.channel()
canal.queue_declare(queue='fila_sensores')  # Alterado para 'fila_sensores'

enviar_dados("SensorFumaca", canal)
