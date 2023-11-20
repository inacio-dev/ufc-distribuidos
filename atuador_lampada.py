# atuador_lampada.py
import grpc
from concurrent import futures
import atuador_pb2
import atuador_pb2_grpc

class AtuadorLampada(atuador_pb2_grpc.AtuadorServicer):
    status = False

    def LigarLampada(self, request, context):
        self.status = True
        print("Lampada Ligada")
        return atuador_pb2.Resposta(status="Lâmpada ligada")

    def DesligarLampada(self, request, context):
        self.status = False
        print("Lampada Ligada")
        return atuador_pb2.Resposta(status="Lâmpada desligada")

def iniciar_servidor():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atuador_pb2_grpc.add_AtuadorServicer_to_server(AtuadorLampada(), servidor)
    servidor.add_insecure_port('[::]:50053')  # Porta diferente para a lâmpada
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
