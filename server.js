const net = require("net");
const sqlite3 = require("sqlite3").verbose();

// Configurações do servidor TCP
const TCP_SERVER_PORT = 5000;

// Configurações do SQLite
const DB_PATH = "./data.db"; // Coloque o caminho desejado para o seu banco de dados SQLite

// Crie o banco de dados e as tabelas (se não existirem)
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error("Erro ao abrir o banco de dados:", err.message);
  } else {
    console.log("Conectado ao banco de dados SQLite");

    // Tabelas para sensores
    db.run(
      "CREATE TABLE IF NOT EXISTS SensorLuminosidade (id INTEGER PRIMARY KEY AUTOINCREMENT, nivel_luminosidade INTEGER, timestamp INTEGER)",
      (createTableError) => {
        if (createTableError) {
          console.error(
            "Erro ao criar a tabela para SensorLuminosidade:",
            createTableError.message
          );
        } else {
          console.log("Tabela para SensorLuminosidade criada ou já existente");
        }
      }
    );

    db.run(
      "CREATE TABLE IF NOT EXISTS SensorTemperatura (id INTEGER PRIMARY KEY AUTOINCREMENT, temperatura REAL, timestamp INTEGER)",
      (createTableError) => {
        if (createTableError) {
          console.error(
            "Erro ao criar a tabela para SensorTemperatura:",
            createTableError.message
          );
        } else {
          console.log("Tabela para SensorTemperatura criada ou já existente");
        }
      }
    );

    db.run(
      "CREATE TABLE IF NOT EXISTS SensorFumaca (id INTEGER PRIMARY KEY AUTOINCREMENT, presenca_fumaca TEXT, timestamp INTEGER)",
      (createTableError) => {
        if (createTableError) {
          console.error(
            "Erro ao criar a tabela para SensorFumaca:",
            createTableError.message
          );
        } else {
          console.log("Tabela para SensorFumaca criada ou já existente");
        }
      }
    );

    // Tabelas para atuadores
    db.run(
      "CREATE TABLE IF NOT EXISTS CommandAquecedor (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, timestamp INTEGER)",
      (createTableError) => {
        if (createTableError) {
          console.error(
            "Erro ao criar a tabela para CommandAquecedor:",
            createTableError.message
          );
        } else {
          console.log("Tabela para CommandAquecedor criada ou já existente");
        }
      }
    );

    db.run(
      "CREATE TABLE IF NOT EXISTS CommandControleIncendio (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, timestamp INTEGER)",
      (createTableError) => {
        if (createTableError) {
          console.error(
            "Erro ao criar a tabela para CommandControleIncendio:",
            createTableError.message
          );
        } else {
          console.log(
            "Tabela para CommandControleIncendio criada ou já existente"
          );
        }
      }
    );

    db.run(
      "CREATE TABLE IF NOT EXISTS CommandLampada (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, timestamp INTEGER)",
      (createTableError) => {
        if (createTableError) {
          console.error(
            "Erro ao criar a tabela para CommandLampada:",
            createTableError.message
          );
        } else {
          console.log("Tabela para CommandLampada criada ou já existente");
        }
      }
    );
  }
});

// Crie um servidor TCP
const server = net.createServer((socket) => {
  console.log("Cliente conectado.");

  // Configurar uma função para processar os dados recebidos do cliente
  socket.on("data", (data) => {
    try {
      const dados = JSON.parse(data.toString());
      console.log("Dados recebidos:", dados);

      // Inserir dados nas tabelas correspondentes
      switch (dados.sensor) {
        // Iniciar o envio dos dados dos atuadores
        case "CommandAquecedor":
          enviarDadosTCP("CommandAquecedor", socket);
          break;
        // Repetir o processo para outros atuadores, se necessário
        case "CommandControleIncendio":
          enviarDadosTCP("CommandControleIncendio", socket);
          break;
        case "CommandLampada":
          enviarDadosTCP("CommandLampada", socket);
          break;

        case "SensorLuminosidade":
          db.run(
            "INSERT INTO SensorLuminosidade (nivel_luminosidade, timestamp) VALUES (?, ?)",
            [dados.dados.nivel_luminosidade, dados.dados.timestamp],
            (insertError) => {
              if (insertError) {
                console.error(
                  "Erro ao inserir dados no SensorLuminosidade:",
                  insertError.message
                );
              } else {
                console.log("Dados inseridos no SensorLuminosidade");
              }
            }
          );
          break;
        case "SensorTemperatura":
          db.run(
            "INSERT INTO SensorTemperatura (temperatura, timestamp) VALUES (?, ?)",
            [dados.dados.temperatura, dados.dados.timestamp],
            (insertError) => {
              if (insertError) {
                console.error(
                  "Erro ao inserir dados no SensorTemperatura:",
                  insertError.message
                );
              } else {
                console.log("Dados inseridos no SensorTemperatura");
              }
            }
          );
          break;
        case "SensorFumaca":
          db.run(
            "INSERT INTO SensorFumaca (presenca_fumaca, timestamp) VALUES (?, ?)",
            [dados.dados.presenca_fumaca, dados.dados.timestamp],
            (insertError) => {
              if (insertError) {
                console.error(
                  "Erro ao inserir dados no SensorFumaca:",
                  insertError.message
                );
              } else {
                console.log("Dados inseridos no SensorFumaca");
              }
            }
          );
          break;
        default:
          console.log("Tipo de sensor desconhecido:", dados.nome);
      }
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

// Função para enviar dados para o HomeAssistant via TCP
function enviarDadosTCP(atuador_nome, socket) {
  // Obter o último valor de um atuador e enviá-lo para o HomeAssistant
  obterUltimoValorAtuador(atuador_nome, (ultimoValor) => {
    try {
      // Preparar os dados a serem enviados
      const dadosEnvio = { atuador: atuador_nome, dados: ultimoValor };

      // Enviar os dados para o servidor TCP do HomeAssistant
      socket.write(JSON.stringify(dadosEnvio));

      console.log(
        `Dados enviados para o HomeAssistant (${atuador_nome}):`,
        dadosEnvio
      );
    } catch (e) {
      console.error(
        `Erro ao enviar dados para o HomeAssistant (${atuador_nome}):`,
        e.message
      );
    }
  });
}

// Função para obter o último valor de um atuador
function obterUltimoValorAtuador(tabela, callback) {
  const query = `SELECT * FROM ${tabela} ORDER BY timestamp DESC LIMIT 1`;

  db.get(query, (err, row) => {
    if (err) {
      console.error(`Erro ao obter o último valor de ${tabela}:`, err.message);
    } else {
      callback(row);
    }
  });
}
