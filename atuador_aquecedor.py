# atuador_aquecedor.py
import grpc
from concurrent import futures
import atuador_pb2
import atuador_pb2_grpc

class AtuadorAquecedor(atuador_pb2_grpc.AtuadorServicer):
    status = False

    def LigarAquecedor(self, request, context):
        self.status = True
        print("Aquecedor ligado")
        return atuador_pb2.Resposta(status="Aquecedor ligado")

    def DesligarAquecedor(self, request, context):
        self.status = False
        print("Aquecedor desligado")
        return atuador_pb2.Resposta(status="Aquecedor desligado")


def iniciar_servidor():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atuador_pb2_grpc.add_AtuadorServicer_to_server(AtuadorAquecedor(), servidor)
    servidor.add_insecure_port('[::]:50052')
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
