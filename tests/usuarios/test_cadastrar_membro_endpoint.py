def payload_membro(**overrides):
    payload = {
        "nome_completo": "Membro de Teste",
        "cpf": "98765432100",
        "vinculo_institucional": "MAT98765",
        "email": "novo.membro@example.com",
        "senha": "SenhaForte123!",
    }
    return payload | overrides


def test_cadastrar_membro_com_sucesso(client):
    resposta = client.post(
        "/usuarios/",
        json=payload_membro(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "Membro"
    assert resposta.json()["ativo"] is True
    assert "senha_codificada" not in resposta.json()


def test_rota_legada_de_cadastro_de_membro_continua_aceita(client):
    resposta = client.post(
        "/usuarios/servidor",
        json=payload_membro(cpf="98765432109", email="legado@example.com"),
    )

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "Membro"


def test_openapi_exibe_cadastro_generico_e_oculta_rota_legada(client):
    schema = client.get("/openapi.json").json()

    assert "post" in schema["paths"]["/usuarios/"]
    assert "/usuarios/servidor" not in schema["paths"]


def test_cadastrar_membro_rejeita_cpf_duplicado(client, usuarios):
    resposta = client.post(
        "/usuarios/",
        json=payload_membro(
            cpf="00000000001",
            email="cpf.duplicado@example.com",
            vinculo_institucional="MAT90001",
        ),
    )

    assert resposta.status_code == 409


def test_cadastrar_membro_rejeita_email_duplicado(client, usuarios):
    resposta = client.post(
        "/usuarios/",
        json=payload_membro(
            cpf="98765432102",
            email="membro@example.com",
            vinculo_institucional="MAT90002",
        ),
    )

    assert resposta.status_code == 409


def test_cadastrar_membro_rejeita_vinculo_duplicado(client, usuarios):
    resposta = client.post(
        "/usuarios/",
        json=payload_membro(
            cpf="98765432103",
            email="vinculo.duplicado@example.com",
            vinculo_institucional="MAT00001",
        ),
    )

    assert resposta.status_code == 409


def test_cadastrar_membro_rejeita_dados_invalidos(client):
    resposta = client.post(
        "/usuarios/",
        json=payload_membro(email="email-invalido", senha="curta"),
    )

    assert resposta.status_code == 422


def test_cadastrar_membro_rejeita_campos_obrigatorios_ausentes(client):
    resposta = client.post(
        "/usuarios/",
        json={"nome_completo": "Membro Incompleto"},
    )

    assert resposta.status_code == 422
