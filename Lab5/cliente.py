import requests


def consumir_api(nome, url):
    try:
        resposta = requests.get(
            url,
            timeout=5
        )

        resposta.raise_for_status()

        dados = resposta.json()

        print(f"--- Resposta do {nome} ---")
        print(f"Mensagem: {dados['mensagem']}")
        print(f"Status: {dados['status']}")
        print(f"Tecnologia: {dados['tecnologia']}")
        print()

    except (
        requests.RequestException,
        ValueError,
        KeyError
    ) as erro:
        print(f"Erro ao consultar {nome}: {erro}")


if __name__ == "__main__":
    consumir_api(
        "Flask",
        "http://localhost:5000/api/data"
    )

    consumir_api(
        "Node.js",
        "http://localhost:3000/api/data"
    )