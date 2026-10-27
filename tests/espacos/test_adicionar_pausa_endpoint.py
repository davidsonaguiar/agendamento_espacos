import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.espacos.conftest import payload_pausa


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR],
)
def test_perfil_autorizado_adiciona_pausa(client, headers, espaco, perfil):
    resposta = client.post(
        f"/espacos/{espaco['id']}/pausas",
        headers=headers[perfil],
        json=payload_pausa(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["motivo"] == "Manutenção preventiva"
    assert resposta.json()["id_espaco"] == espaco["id"]


def test_adicionar_pausa_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.post(
        f"/espacos/{espaco['id']}/pausas",
        json=payload_pausa(),
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_adicionar_pausa_rejeita_perfil_sem_permissao(
    client, headers, espaco, perfil
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/pausas",
        headers=headers[perfil],
        json=payload_pausa(),
    )

    assert resposta.status_code == 403


def test_adicionar_pausa_rejeita_espaco_inexistente(client, headers):
    resposta = client.post(
        "/espacos/99999/pausas",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_pausa(),
    )

    assert resposta.status_code == 404


def test_adicionar_pausa_rejeita_motivo_curto(client, headers, espaco):
    resposta = client.post(
        f"/espacos/{espaco['id']}/pausas",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_pausa(motivo="ab"),
    )

    assert resposta.status_code == 422


def test_adicionar_pausa_rejeita_data_invalida(client, headers, espaco):
    resposta = client.post(
        f"/espacos/{espaco['id']}/pausas",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_pausa(data_inicio="2027-01-15", data_fim="2027-01-10"),
    )

    assert resposta.status_code == 422
