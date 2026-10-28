from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def payload_interno(**overrides):
    payload = {
        "nome_completo": "Monitor Criado",
        "cpf": "98765432110",
        "vinculo_institucional": "MAT98770",
        "email": "monitor.criado@example.com",
        "senha": "SenhaForte123!",
        "perfil": PerfilUsuario.MONITOR.value,
    }
    return payload | overrides


def test_administrador_cadastra_usuario_interno(client, headers):
    resposta = client.post(
        "/usuarios/interno",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_interno(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == PerfilUsuario.MONITOR.value


def test_coordenador_cadastra_monitor(client, headers):
    resposta = client.post(
        "/usuarios/interno",
        headers=headers[PerfilUsuario.COORDENADOR],
        json=payload_interno(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["perfil"] == PerfilUsuario.MONITOR.value


def test_coordenador_nao_pode_cadastrar_administrador_ou_coordenador(
    client, headers
):
    for perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR):
        resposta = client.post(
            "/usuarios/interno",
            headers=headers[PerfilUsuario.COORDENADOR],
            json=payload_interno(
                cpf="98765432111" if perfil == PerfilUsuario.ADMINISTRADOR else "98765432112",
                vinculo_institucional=(
                    "MAT98771"
                    if perfil == PerfilUsuario.ADMINISTRADOR
                    else "MAT98772"
                ),
                email=f"{perfil.name.lower()}.criado@example.com",
                perfil=perfil.value,
            ),
        )

        assert resposta.status_code == 403


def test_usuario_sem_perfil_autorizado_nao_cadastra_usuario_interno(
    client, headers
):
    resposta = client.post(
        "/usuarios/interno",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_interno(),
    )

    assert resposta.status_code == 403


def test_cadastro_interno_rejeita_requisicao_sem_token(client):
    resposta = client.post(
        "/usuarios/interno",
        json=payload_interno(),
    )

    assert resposta.status_code == 401


def test_cadastro_interno_rejeita_dados_invalidos(client, headers):
    resposta = client.post(
        "/usuarios/interno",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_interno(email="invalido", senha="curta"),
    )

    assert resposta.status_code == 422


def test_cadastro_interno_rejeita_identificadores_duplicados(client, headers):
    resposta = client.post(
        "/usuarios/interno",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_interno(
            cpf="00000000001",
            vinculo_institucional="MAT98773",
            email="cpf.duplicado.interno@example.com",
        ),
    )

    assert resposta.status_code == 409
