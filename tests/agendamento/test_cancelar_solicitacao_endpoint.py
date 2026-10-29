from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao


def test_solicitante_cancela_sua_solicitacao(client, headers, solicitacao):
    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Cancelada"


def test_administrador_cancela_solicitacao_de_outro_usuario(
    client, headers, solicitacao
):
    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Cancelada"


def test_usuario_que_nao_e_solicitante_nao_cancela_solicitacao(
    client, headers, solicitacao
):
    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 403


def test_cancelar_solicitacao_inexistente_retorna_nao_encontrado(
    client, headers
):
    resposta = client.patch(
        "/solicitacoes/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_solicitacao_cancelada_nao_pode_ser_cancelada_novamente(
    client, headers, solicitacao
):
    primeira = client.patch(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )
    segunda = client.patch(
        f"/solicitacoes/{solicitacao['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 409


def test_cancelar_solicitacao_rejeita_requisicao_sem_token(
    client, solicitacao
):
    resposta = client.patch(f"/solicitacoes/{solicitacao['id']}")

    assert resposta.status_code == 401
