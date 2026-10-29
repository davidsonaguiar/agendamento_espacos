import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.espacos.conftest import payload_recurso


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR],
)
def test_perfil_autorizado_cria_recurso_associado_ao_espaco(
    client, headers, espaco, perfil
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[perfil],
        json=payload_recurso(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["id_espaco"] == espaco["id"]
    assert resposta.json()["disponibilidade"] is True


def test_criar_recurso_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.post(
        f"/espacos/{espaco['id']}/recursos",
        json=payload_recurso(),
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_criar_recurso_rejeita_perfil_sem_permissao(
    client, headers, espaco, perfil
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[perfil],
        json=payload_recurso(),
    )

    assert resposta.status_code == 403


def test_criar_recurso_rejeita_espaco_inexistente(client, headers):
    resposta = client.post(
        "/espacos/99999/recursos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_recurso(),
    )

    assert resposta.status_code == 404


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": ""},
        {"tipo": ""},
        {"nome": "n" * 101},
    ],
)
def test_criar_recurso_rejeita_dados_invalidos(
    client, headers, espaco, dados
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_recurso(**dados),
    )

    assert resposta.status_code == 422
