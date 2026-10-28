import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR],
)
def test_perfil_autorizado_remove_pausa(
    client, headers, espaco, pausa, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/pausas/{pausa['id']}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 200


def test_remover_pausa_rejeita_requisicao_sem_token(
    client, espaco, pausa
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/pausas/{pausa['id']}"
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_remover_pausa_rejeita_perfil_sem_permissao(
    client, headers, espaco, pausa, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/pausas/{pausa['id']}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_remover_pausa_inexistente_retorna_nao_encontrado(
    client, headers, espaco
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/pausas/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_remover_pausa_de_espaco_inexistente_retorna_nao_encontrado(
    client, headers, pausa
):
    resposta = client.delete(
        f"/espacos/99999/pausas/{pausa['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404
