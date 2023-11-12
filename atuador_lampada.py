# atuador_lampada.py
import grpc
from concurrent import futures
import atuador_pb2
import atuador_pb2_grpc

class AtuadorLampada(atuador_pb2_grpc.AtuadorServicer):
    status = False

    def ligarLampada(self, request, context):
        self.status = True
        return atuador_pb2.Resposta(status="Lâmpada ligada")

    def desligarLampada(self, request, context):
        self.status = False
        return atuador_pb2.Resposta(status="Lâmpada desligada")

def iniciar_servidor():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atuador_pb2_grpc.add_AtuadorServicer_to_server(AtuadorLampada(), servidor)
    servidor.add_insecure_port('[::]:50052')
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
