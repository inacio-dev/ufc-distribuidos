import time
import random
import json
import pika

def enviar_dados(sensor_nome, canal):
    while True:
        nivel_luminosidade = random.randint(0, 100)
        mensagem = {
            'nome': sensor_nome,  # Alterado para 'nome' para corresponder à estrutura esperada pelo HomeAssistant
            'dados': {
                'nivel_luminosidade': nivel_luminosidade,
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

enviar_dados("SensorLuminosidade", canal)
