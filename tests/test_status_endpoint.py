def test_status_endpoint(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"]
