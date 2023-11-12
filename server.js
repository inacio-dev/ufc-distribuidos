const net = require("net");

// Configurações do servidor TCP
const TCP_SERVER_PORT = 5000;

// Crie um servidor TCP
const server = net.createServer((socket) => {
  console.log("Cliente conectado.");

  // Configurar uma função para processar os dados recebidos do cliente
  socket.on("data", (data) => {
    try {
      const dados = JSON.parse(data.toString());
      console.log("Dados recebidos:", dados);
    } catch (error) {
      console.error("Erro ao processar dados:", error.message);
    }
  });

  // Configurar uma função para lidar com a desconexão do cliente
  socket.on("end", () => {
    console.log("Cliente desconectado.");
  });
});

// Iniciar o servidor TCP na porta especificada
server.listen(TCP_SERVER_PORT, () => {
  console.log(`Servidor TCP rodando na porta ${TCP_SERVER_PORT}`);
});
