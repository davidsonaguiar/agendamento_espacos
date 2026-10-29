from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_solicitante_obtem_sua_solicitacao(client, headers, solicitacao):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["id"] == solicitacao["id"]


def test_administrador_obtem_solicitacao_de_outro_usuario(
    client, headers, solicitacao
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["id"] == solicitacao["id"]


def test_coordenador_obtem_solicitacao_de_outro_usuario(
    client, headers, solicitacao
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 200


def test_usuario_sem_permissao_nao_obtem_solicitacao_alheia(
    client, headers, solicitacao
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.MONITOR],
    )

    assert resposta.status_code == 403


def test_obter_solicitacao_inexistente_retorna_nao_encontrado(
    client, headers
):
    resposta = client.get(
        "/solicitacoes/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_obter_solicitacao_rejeita_requisicao_sem_token(
    client, solicitacao
):
    resposta = client.get(f"/solicitacoes/{solicitacao['id']}")

    assert resposta.status_code == 401
