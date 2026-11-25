from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_login_com_email_e_senha_validos(client, usuarios):
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "membro@example.com",
            "senha": "SenhaValida123!",
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["access_token"]
    assert corpo["token_type"] == "bearer"
    assert corpo["usuario"]["perfil"] == PerfilUsuario.MEMBRO.value
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
            "identificacao": "membro@example.com",
            "senha": "SenhaErrada123!",
        },
    )

    assert resposta.status_code == 401


def test_login_bloqueia_identificacao_e_ip_apos_cinco_falhas(client):
    dados = {
        "identificacao": "membro@example.com",
        "senha": "SenhaErrada123!",
    }

    respostas = [client.post("/usuarios/login", json=dados) for _ in range(5)]

    assert [resposta.status_code for resposta in respostas] == [401] * 5
    bloqueio = client.post("/usuarios/login", json=dados)
    assert bloqueio.status_code == 429
    assert bloqueio.headers["retry-after"]


def test_login_valido_limpa_falhas_acumuladas(client, usuarios):
    dados = {
        "identificacao": "membro@example.com",
        "senha": "SenhaErrada123!",
    }
    for _ in range(4):
        assert client.post("/usuarios/login", json=dados).status_code == 401

    resposta_valida = client.post(
        "/usuarios/login",
        json={**dados, "senha": "SenhaValida123!"},
    )
    assert resposta_valida.status_code == 200
    assert client.post("/usuarios/login", json=dados).status_code == 401


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
        json={"identificacao": "membro@example.com"},
    )

    assert resposta.status_code == 422
