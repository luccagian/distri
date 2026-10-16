import requests


def consultar(url):
    resposta = requests.get(
        url,
        timeout=5
    )

    resposta.raise_for_status()

    return resposta.json()


def consultar_produto(id):
    dados_fiscais = consultar(
        f"http://localhost:5000/detalhes/{id}"
    )

    dados_estoque = consultar(
        f"http://localhost:3000/estoque/{id}"
    )

    return {
        "id": id,
        **dados_fiscais,
        **dados_estoque
    }


def monitorar_servicos(urls):
    for url in urls:
        try:
            dados = consultar(url)

            print(f"Serviço: {dados['service']}")
            print(f"Status: {dados['status']}")
            print(f"Timestamp: {dados['timestamp']}")
            print()

        except (
            requests.RequestException,
            ValueError,
            KeyError
        ) as erro:
            print(f"Falha ao consultar {url}: {erro}")
            print()


if __name__ == "__main__":
    id = input("Informe o ID do produto: ").strip()

    try:
        produto = consultar_produto(id)

        print()
        print(
            f"ID: {produto['id']} | "
            f"Nome: {produto['nome']} | "
            f"Preço: R$ {produto['preco']} | "
            f"Estoque: {produto['estoque']}"
        )

    except (
        requests.RequestException,
        ValueError,
        KeyError
    ) as erro:
        print(f"Erro ao consultar produto: {erro}")

    print()
    print("--- Monitoramento dos serviços ---")

    monitorar_servicos([
        "http://localhost:5000/status",
        "http://localhost:3000/status"
    ])