from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_obter_dados_pessoais_com_token_valido(client, headers, usuarios):
    resposta = client.get(
        "/usuarios/me",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["id"] == usuarios[PerfilUsuario.SERVIDOR]
    assert resposta.json()["perfil"] == PerfilUsuario.SERVIDOR.value
    assert "senha_codificada" not in resposta.json()


def test_obter_dados_pessoais_rejeita_requisicao_sem_token(client):
    resposta = client.get("/usuarios/me")

    assert resposta.status_code == 401


def test_obter_dados_pessoais_rejeita_token_invalido(client):
    resposta = client.get(
        "/usuarios/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401
