const express = require("express");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const port = 3000;

// Configurações do SQLite
const DB_PATH = "./data.db";
const db = new sqlite3.Database(DB_PATH);

app.use(express.json());

// Configurar rota para servir uma página HTML simples
app.get("/", (req, res) => {
  res.sendFile(__dirname + "/index.html");
});

// Configurar rota para obter dados do sensor de luminosidade
app.get("/SensorLuminosidade", (req, res) => {
  db.all(
    "SELECT * FROM SensorLuminosidade ORDER BY timestamp DESC LIMIT 1",
    (err, rows) => {
      if (err) {
        console.error(
          "Erro ao buscar dados do SensorLuminosidade:",
          err.message
        );
        res
          .status(500)
          .json({ error: "Erro ao buscar dados do SensorLuminosidade" });
      } else {
        res.json(rows[0]);
      }
    }
  );
});

// Configurar rota para obter dados do sensor de temperatura
app.get("/SensorTemperatura", (req, res) => {
  db.all(
    "SELECT * FROM SensorTemperatura ORDER BY timestamp DESC LIMIT 1",
    (err, rows) => {
      if (err) {
        console.error(
          "Erro ao buscar dados do SensorTemperatura:",
          err.message
        );
        res
          .status(500)
          .json({ error: "Erro ao buscar dados do SensorTemperatura" });
      } else {
        res.json(rows[0]);
      }
    }
  );
});

// Configurar rota para obter dados do sensor de fumaça
app.get("/SensorFumaca", (req, res) => {
  db.all(
    "SELECT * FROM SensorFumaca ORDER BY timestamp DESC LIMIT 1",
    (err, rows) => {
      if (err) {
        console.error("Erro ao buscar dados do SensorFumaca:", err.message);
        res.status(500).json({ error: "Erro ao buscar dados do SensorFumaca" });
      } else {
        res.json(rows[0]);
      }
    }
  );
});

// Configurar rota para lidar com comandos dos atuadores
app.put("/:actuator", (req, res) => {
  const { actuator } = req.params;
  const { command } = req.body;

  // Registra o último comando na tabela correspondente ao atuador
  const commandTable = `Command${
    actuator.charAt(0).toUpperCase() + actuator.slice(1)
  }`;
  db.run(`INSERT INTO ${commandTable} (command, timestamp) VALUES (?, ?)`, [
    command,
    Date.now(),
  ]);

  res.json({ status: "Comando recebido com sucesso" });
});

// Configurar rota para obter status do aquecedor
app.get("/aquecedor/status", (req, res) => {
  db.get(
    "SELECT * FROM CommandAquecedor ORDER BY timestamp DESC LIMIT 1",
    (err, row) => {
      if (err) {
        console.error("Erro ao buscar status do aquecedor:", err.message);
        res.status(500).json({ error: "Erro ao buscar status do aquecedor" });
      } else {
        res.json({ status: row ? row.command : "Desconhecido" });
      }
    }
  );
});

// Configurar rota para obter status do controle de incêndio
app.get("/controle-incendio/status", (req, res) => {
  db.get(
    "SELECT * FROM CommandControleIncendio ORDER BY timestamp DESC LIMIT 1",
    (err, row) => {
      if (err) {
        console.error(
          "Erro ao buscar status do controle de incêndio:",
          err.message
        );
        res
          .status(500)
          .json({ error: "Erro ao buscar status do controle de incêndio" });
      } else {
        res.json({ status: row ? row.command : "Desconhecido" });
      }
    }
  );
});

// Configurar rota para obter status da lâmpada
app.get("/lampada/status", (req, res) => {
  db.get(
    "SELECT * FROM CommandLampada ORDER BY timestamp DESC LIMIT 1",
    (err, row) => {
      if (err) {
        console.error("Erro ao buscar status da lâmpada:", err.message);
        res.status(500).json({ error: "Erro ao buscar status da lâmpada" });
      } else {
        res.json({ status: row ? row.command : "Desconhecido" });
      }
    }
  );
});

// Iniciar o servidor
app.listen(port, () => {
  console.log(`Servidor HTTP rodando na porta ${port}`);
});
