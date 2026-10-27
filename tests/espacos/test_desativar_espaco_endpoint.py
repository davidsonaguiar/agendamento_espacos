import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_administrador_desativa_espaco(client, headers, espaco):
    resposta = client.delete(
        f"/espacos/{espaco['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["disponibilidade"] is False


def test_desativar_espaco_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.delete(f"/espacos/{espaco['id']}")

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [
        PerfilUsuario.COORDENADOR,
        PerfilUsuario.MONITOR,
        PerfilUsuario.SERVIDOR,
        PerfilUsuario.ALUNO,
    ],
)
def test_desativar_espaco_rejeita_perfil_sem_permissao(
    client, headers, espaco, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_desativar_espaco_inexistente_retorna_nao_encontrado(client, headers):
    resposta = client.delete(
        "/espacos/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404
