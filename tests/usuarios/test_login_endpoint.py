from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_login_com_email_e_senha_validos(client, usuarios):
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "servidor@example.com",
            "senha": "SenhaValida123!",
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["access_token"]
    assert corpo["token_type"] == "bearer"
    assert corpo["usuario"]["perfil"] == PerfilUsuario.SERVIDOR.value
    assert "senha_codificada" not in corpo["usuario"]


def test_login_com_cpf_formatado_e_senha_validos(client, usuarios):
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "000.000.00-003",
            "senha": "SenhaValida123!",
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["usuario"]["cpf"] == "00000000003"


def test_login_rejeita_senha_incorreta(client):
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "servidor@example.com",
            "senha": "SenhaErrada123!",
        },
    )

    assert resposta.status_code == 401


def test_login_rejeita_identificacao_inexistente(client):
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "nao.existe@example.com",
            "senha": "SenhaValida123!",
        },
    )

    assert resposta.status_code == 401


def test_login_rejeita_payload_incompleto(client):
    resposta = client.post(
        "/usuarios/login",
        json={"identificacao": "servidor@example.com"},
    )

    assert resposta.status_code == 422
