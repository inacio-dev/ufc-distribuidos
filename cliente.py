import requests

# Enviar comando para os atuadores
comando = {"comando": "ligar"}
response = requests.post("http://seu-servidor:5000/enviar-comando", json=comando)
print(response.json())

# Obter dados dos sensores
response = requests.get("http://seu-servidor:5000/dados-sensores")
dados_sensores = response.json()
print(dados_sensores)
