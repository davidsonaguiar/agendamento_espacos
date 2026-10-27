from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def adicionar_participante(
    client, headers, id_projeto: int, id_usuario: int
):
    resposta = client.post(
        f"/projetos/{id_projeto}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "id_usuario": id_usuario,
            "papel_no_projeto": "Colaborador",
        },
    )
    assert resposta.status_code == 201, resposta.text


def test_responsavel_remove_participante(
    client, headers, usuarios, projeto
):
    id_participante = usuarios[PerfilUsuario.MONITOR]
    adicionar_participante(client, headers, projeto["id"], id_participante)

    resposta = client.delete(
        f"/projetos/{projeto['id']}/participantes/{id_participante}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert all(
        participante["id_usuario"] != id_participante
        for participante in resposta.json()["participantes"]
    )


def test_administrador_remove_participante(
    client, headers, usuarios, projeto
):
    id_participante = usuarios[PerfilUsuario.MONITOR]
    adicionar_participante(client, headers, projeto["id"], id_participante)

    resposta = client.delete(
        f"/projetos/{projeto['id']}/participantes/{id_participante}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200


def test_usuario_que_nao_e_responsavel_nao_remove_participante(
    client, headers, usuarios, projeto
):
    id_participante = usuarios[PerfilUsuario.MONITOR]
    adicionar_participante(client, headers, projeto["id"], id_participante)

    resposta = client.delete(
        f"/projetos/{projeto['id']}/participantes/{id_participante}",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 403


def test_remover_usuario_que_nao_e_participante_retorna_nao_encontrado(
    client, headers, usuarios, projeto
):
    resposta = client.delete(
        f"/projetos/{projeto['id']}/participantes/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_remover_participante_de_projeto_inexistente(
    client, headers, usuarios
):
    resposta = client.delete(
        f"/projetos/99999/participantes/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_remover_participante_rejeita_requisicao_sem_token(
    client, usuarios, projeto
):
    resposta = client.delete(
        f"/projetos/{projeto['id']}/participantes/{usuarios[PerfilUsuario.MONITOR]}"
    )

    assert resposta.status_code == 401
