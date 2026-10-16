const express = require("express");

const app = express();

app.use(express.json());

const FISCAL_URL =
  process.env.FISCAL_URL || "http://127.0.0.1:5000";

const produtos_estoque = {
  "1": {
    nome: "Dell XPS 13",
    estoque: 10
  },
  "2": {
    nome: "Monitor LG 29",
    estoque: 5
  }
};

// O exercício 4 utiliza outro nome.
// O alias mantém os dados na mesma estrutura.
const produtos_comerciais = produtos_estoque;

// Impede dois cadastros simultâneos do mesmo ID
// dentro desta instância do Node.
const cadastrosEmAndamento = new Set();

function idValido(id) {
  return (
    typeof id === "string" &&
    /^[1-9][0-9]*$/.test(id)
  );
}

function erroId(res) {
  return res.status(400).json({
    error: "INVALID_ID",
    message: "O ID deve ser um inteiro positivo"
  });
}

async function chamarFiscal(caminho, opcoes = {}) {
  return fetch(FISCAL_URL + caminho, {
    ...opcoes,
    signal: AbortSignal.timeout(3000)
  });
}

// Exemplo inicial da aula
app.get("/api/data", (req, res) => {
  res.json({
    mensagem: "Olá do Node.js!",
    status: "sucesso",
    tecnologia: "JavaScript"
  });
});

// Exercício 1: consulta ao estoque
app.get("/estoque/:id", (req, res) => {
  const { id } = req.params;

  if (!idValido(id)) {
    return erroId(res);
  }

  const produto = produtos_estoque[id];

  if (!produto) {
    return res.status(404).json({
      error: "NOT_FOUND",
      message: "Produto não encontrado"
    });
  }

  return res.status(200).json(produto);
});

// Exercício 2: proxy e integração server-to-server
app.get("/api/full-info/:id", async (req, res) => {
  const { id } = req.params;

  if (!idValido(id)) {
    return erroId(res);
  }

  const produto = produtos_estoque[id];

  if (!produto) {
    return res.status(404).json({
      error: "NOT_FOUND",
      message: "Produto não encontrado"
    });
  }

  try {
    const resposta = await chamarFiscal(
      `/detalhes/${id}`
    );

    if (!resposta.ok) {
      return res.status(502).json({
        error: "UPSTREAM_ERROR",
        message: "Consulta fiscal falhou"
      });
    }

    const dadosFiscais = await resposta.json();

    return res.status(200).json({
      id,
      ...produto,
      ...dadosFiscais
    });
  } catch (erro) {
    return res.status(503).json({
      error: "FISCAL_UNAVAILABLE",
      message: "Serviço fiscal indisponível"
    });
  }
});

// Exercício 3: contrato de monitoramento
app.get("/status", (req, res) => {
  res.status(200).json({
    service: "node-estoque",
    status: "online",
    timestamp: new Date().toISOString()
  });
});

// Exercício 4: cadastro integrado
app.post("/cadastrar", async (req, res) => {
  const dados = req.body;

  if (
    !dados ||
    typeof dados !== "object" ||
    Array.isArray(dados)
  ) {
    return res.status(400).json({
      error: "INVALID_BODY",
      message: "Envie um objeto JSON"
    });
  }

  const {
    id,
    nome,
    estoque,
    preco_base,
    categoria
  } = dados;

  if (!idValido(id)) {
    return erroId(res);
  }

  const dadosInvalidos =
    typeof nome !== "string" ||
    !nome.trim() ||
    !Number.isInteger(estoque) ||
    estoque < 0 ||
    typeof preco_base !== "number" ||
    !Number.isFinite(preco_base) ||
    preco_base < 0 ||
    typeof categoria !== "string" ||
    !categoria.trim();

  if (dadosInvalidos) {
    return res.status(400).json({
      error: "INVALID_DATA",
      message: "Dados comerciais ou fiscais inválidos"
    });
  }

  if (
    produtos_comerciais[id] ||
    cadastrosEmAndamento.has(id)
  ) {
    return res.status(409).json({
      error: "DUPLICATE_ID",
      message: "ID já cadastrado ou em processamento"
    });
  }

  const nomeMaiusculo = nome.trim().toUpperCase();

  cadastrosEmAndamento.add(id);

  try {
    const resposta = await chamarFiscal(
      "/fiscal/cadastrar",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          id,
          preco_base,
          categoria
        })
      }
    );

    if (resposta.status !== 201) {
      const codigo =
        resposta.status === 409 ? 409 : 502;

      return res.status(codigo).json({
        error: "FISCAL_REJECTED",
        message: "Cadastro fiscal recusado"
      });
    }

    const dadosFiscais = await resposta.json();

    // Grava somente após confirmação fiscal 201.
    produtos_comerciais[id] = {
      nome: nomeMaiusculo,
      estoque
    };

    return res.status(201).json({
      id,
      ...produtos_comerciais[id],
      preco: dadosFiscais.preco,
      categoria: dadosFiscais.categoria
    });
  } catch (erro) {
    return res.status(503).json({
      error: "FISCAL_UNAVAILABLE",
      message: "Serviço fiscal indisponível"
    });
  } finally {
    cadastrosEmAndamento.delete(id);
  }
});

// Tratamento de JSON malformado
app.use((erro, req, res, next) => {
  if (erro.type === "entity.parse.failed") {
    return res.status(400).json({
      error: "INVALID_JSON",
      message: "JSON inválido"
    });
  }

  next(erro);
});

app.listen(3000, "0.0.0.0", () => {
  console.log(
    "Servidor Node rodando em http://localhost:3000"
  );
});