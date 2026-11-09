from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from tests.agendamento.conftest import criar_solicitacao


def test_solicitante_obtem_sua_solicitacao(client, headers, solicitacao):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.MEMBRO],
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
        headers=headers[PerfilEspaco.COORDENADOR],
    )

    assert resposta.status_code == 200


def test_coordenador_nao_obtem_solicitacao_de_outro_espaco(
    client, headers, solicitacao
):
    resposta_outro_espaco = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"nome": "Outro espaço"},
    )
    assert resposta_outro_espaco.status_code == 201
    solicitacao_de_outro_espaco = criar_solicitacao(
        client, headers, resposta_outro_espaco.json()["id"]
    )

    resposta = client.get(
        f"/solicitacoes/{solicitacao_de_outro_espaco['id']}",
        headers=headers[PerfilEspaco.COORDENADOR],
    )

    assert resposta.status_code == 403


def test_usuario_sem_permissao_nao_obtem_solicitacao_alheia(
    client, headers, solicitacao
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilEspaco.MONITOR],
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
