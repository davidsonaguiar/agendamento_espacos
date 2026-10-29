from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def payload_participante(id_usuario: int, **overrides):
    return {
        "id_usuario": id_usuario,
        "papel_no_projeto": "Colaborador",
    } | overrides


def test_responsavel_adiciona_participante(
    client, headers, usuarios, projeto
):
    resposta = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_participante(usuarios[PerfilUsuario.MONITOR]),
    )

    assert resposta.status_code == 201
    assert any(
        participante["id_usuario"] == usuarios[PerfilUsuario.MONITOR]
        for participante in resposta.json()["participantes"]
    )


def test_administrador_adiciona_participante(
    client, headers, usuarios, projeto
):
    resposta = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_participante(usuarios[PerfilUsuario.MONITOR]),
    )

    assert resposta.status_code == 201


def test_usuario_que_nao_e_responsavel_nao_adiciona_participante(
    client, headers, usuarios, projeto
):
    resposta = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.COORDENADOR],
        json=payload_participante(usuarios[PerfilUsuario.MONITOR]),
    )

    assert resposta.status_code == 403


def test_adicionar_participante_rejeita_usuario_inexistente(
    client, headers, projeto
):
    resposta = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_participante(99999),
    )

    assert resposta.status_code == 404


def test_adicionar_participante_duplicado_retorna_conflito(
    client, headers, usuarios, projeto
):
    dados = payload_participante(usuarios[PerfilUsuario.MONITOR])
    primeira = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=dados,
    )
    segunda = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=dados,
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 409


def test_adicionar_participante_rejeita_projeto_inexistente(
    client, headers, usuarios
):
    resposta = client.post(
        "/projetos/99999/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_participante(usuarios[PerfilUsuario.MONITOR]),
    )

    assert resposta.status_code == 404


def test_adicionar_participante_rejeita_payload_invalido(
    client, headers, projeto
):
    resposta = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"id_usuario": 1, "papel_no_projeto": "x"},
    )

    assert resposta.status_code == 422


def test_adicionar_participante_rejeita_requisicao_sem_token(
    client, usuarios, projeto
):
    resposta = client.post(
        f"/projetos/{projeto['id']}/participantes",
        json=payload_participante(usuarios[PerfilUsuario.MONITOR]),
    )

    assert resposta.status_code == 401
