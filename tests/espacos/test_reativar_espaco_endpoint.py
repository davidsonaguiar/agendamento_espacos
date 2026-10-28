import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_administrador_reativa_espaco(client, headers, espaco_inativo):
    resposta = client.patch(
        f"/espacos/{espaco_inativo['id']}/reativar",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["disponibilidade"] is True


def test_reativar_espaco_rejeita_requisicao_sem_token(client, espaco_inativo):
    resposta = client.patch(
        f"/espacos/{espaco_inativo['id']}/reativar"
    )

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
def test_reativar_espaco_rejeita_perfil_sem_permissao(
    client, headers, espaco_inativo, perfil
):
    resposta = client.patch(
        f"/espacos/{espaco_inativo['id']}/reativar",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_reativar_espaco_inexistente_retorna_nao_encontrado(client, headers):
    resposta = client.patch(
        "/espacos/99999/reativar",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_espaco_ativo_nao_pode_ser_reativado(client, headers, espaco):
    resposta = client.patch(
        f"/espacos/{espaco['id']}/reativar",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 409
