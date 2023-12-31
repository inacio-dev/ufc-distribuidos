# atuador_controle_incendio.py
import grpc
from concurrent import futures
import atuador_pb2
import atuador_pb2_grpc

class AtuadorControleIncendio(atuador_pb2_grpc.AtuadorServicer):
    status = False

    def LigarControleIncendio(self, request, context):
        self.status = True
        print("Controle de Incendio Ativado")
        return atuador_pb2.Resposta(status="Controle de incêndio ativado")

    def DesligarControleIncendio(self, request, context):
        self.status = False
        print("Controle de Incendio Desativado")
        return atuador_pb2.Resposta(status="Controle de incêndio desativado")

def iniciar_servidor():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atuador_pb2_grpc.add_AtuadorServicer_to_server(AtuadorControleIncendio(), servidor)
    servidor.add_insecure_port('[::]:50052')  # Porta diferente para o controle de incêndio
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
