import math
import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from flask import Flask, jsonify, request

app = Flask(__name__)

produtos_fiscais = {
    "1": {
        "preco": 2500.0,
        "categoria": "Laptops"
    },
    "2": {
        "preco": 1200.0,
        "categoria": "Monitores"
    }
}

# O exercício 4 utiliza outro nome.
# O alias mantém os dados na mesma estrutura.
produtos_tecnicos = produtos_fiscais


def id_valido(id):
    return (
        isinstance(id, str)
        and re.fullmatch(r"[1-9][0-9]*", id) is not None
    )


def erro_id():
    return jsonify({
        "error": "INVALID_ID",
        "message": "O ID deve ser um inteiro positivo"
    }), 400


# Exemplo inicial da aula
@app.get("/api/data")
def exemplo():
    return jsonify({
        "mensagem": "Olá do Flask!",
        "status": "sucesso",
        "tecnologia": "Python"
    })


# Exercícios 1 e 2: consulta fiscal
@app.get("/detalhes/<id>")
def detalhes(id):
    if not id_valido(id):
        return erro_id()

    produto = produtos_fiscais.get(id)

    if produto is None:
        return jsonify({
            "error": "NOT_FOUND",
            "message": "Produto não encontrado"
        }), 404

    return jsonify(produto), 200


# Exercício 3: contrato de monitoramento
@app.get("/status")
def status():
    timestamp = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    return jsonify({
        "service": "flask-fiscal",
        "status": "online",
        "timestamp": timestamp
    }), 200


# Exercício 4: cadastro fiscal
@app.post("/fiscal/cadastrar")
def cadastrar_fiscal():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "error": "INVALID_BODY",
            "message": "Envie um objeto JSON"
        }), 400

    id = dados.get("id")

    if not id_valido(id):
        return erro_id()

    preco_base = dados.get("preco_base")
    categoria = dados.get("categoria")

    preco_invalido = (
        isinstance(preco_base, bool)
        or not isinstance(preco_base, (int, float))
        or not math.isfinite(preco_base)
        or preco_base < 0
    )

    categoria_invalida = (
        not isinstance(categoria, str)
        or not categoria.strip()
    )

    if preco_invalido or categoria_invalida:
        return jsonify({
            "error": "INVALID_DATA",
            "message": "Preço ou categoria inválidos"
        }), 400

    if id in produtos_tecnicos:
        return jsonify({
            "error": "DUPLICATE_ID",
            "message": "ID já cadastrado"
        }), 409

    preco_calculado = (
        Decimal(str(preco_base)) * Decimal("1.20")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    produtos_tecnicos[id] = {
        "preco": float(preco_calculado),
        "categoria": categoria.strip()
    }

    return jsonify({
        "id": id,
        **produtos_tecnicos[id]
    }), 201


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )