import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR],
)
def test_perfil_autorizado_indisponibiliza_recurso(
    client, headers, espaco, recurso, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/recursos/{recurso['id']}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 200
    assert resposta.json()["disponibilidade"] is False


def test_indisponibilizar_recurso_rejeita_requisicao_sem_token(
    client, espaco, recurso
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/recursos/{recurso['id']}"
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_indisponibilizar_recurso_rejeita_perfil_sem_permissao(
    client, headers, espaco, recurso, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/recursos/{recurso['id']}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_indisponibilizar_recurso_rejeita_espaco_inexistente(
    client, headers, recurso
):
    resposta = client.delete(
        f"/espacos/99999/recursos/{recurso['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_indisponibilizar_recurso_inexistente_retorna_nao_encontrado(
    client, headers, espaco
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/recursos/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404
