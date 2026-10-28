def payload_servidor(**overrides):
    payload = {
        "nome_completo": "Servidor de Teste",
        "cpf": "98765432100",
        "vinculo_institucional": "MAT98765",
        "email": "novo.servidor@example.com",
        "senha": "SenhaForte123!",
    }
    return payload | overrides


def test_cadastrar_servidor_com_sucesso(client):
    resposta = client.post(
        "/usuarios/servidor",
        json=payload_servidor(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == "Servidor"
    assert resposta.json()["ativo"] is True
    assert "senha_codificada" not in resposta.json()


def test_cadastrar_servidor_rejeita_cpf_duplicado(client, usuarios):
    resposta = client.post(
        "/usuarios/servidor",
        json=payload_servidor(
            cpf="00000000001",
            email="cpf.duplicado@example.com",
            vinculo_institucional="MAT90001",
        ),
    )

    assert resposta.status_code == 409


def test_cadastrar_servidor_rejeita_email_duplicado(client, usuarios):
    resposta = client.post(
        "/usuarios/servidor",
        json=payload_servidor(
            cpf="98765432102",
            email="servidor@example.com",
            vinculo_institucional="MAT90002",
        ),
    )

    assert resposta.status_code == 409


def test_cadastrar_servidor_rejeita_vinculo_duplicado(client, usuarios):
    resposta = client.post(
        "/usuarios/servidor",
        json=payload_servidor(
            cpf="98765432103",
            email="vinculo.duplicado@example.com",
            vinculo_institucional="MAT00001",
        ),
    )

    assert resposta.status_code == 409


def test_cadastrar_servidor_rejeita_dados_invalidos(client):
    resposta = client.post(
        "/usuarios/servidor",
        json=payload_servidor(email="email-invalido", senha="curta"),
    )

    assert resposta.status_code == 422


def test_cadastrar_servidor_rejeita_campos_obrigatorios_ausentes(client):
    resposta = client.post(
        "/usuarios/servidor",
        json={"nome_completo": "Servidor Incompleto"},
    )

    assert resposta.status_code == 422
