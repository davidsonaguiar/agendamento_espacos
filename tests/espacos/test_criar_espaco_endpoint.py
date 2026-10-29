import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.espacos.conftest import payload_espaco


def test_administrador_cria_espaco(client, headers):
    resposta = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_espaco(),
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Espaço de teste"
    assert resposta.json()["disponibilidade"] is True


def test_criar_espaco_rejeita_requisicao_sem_token(client):
    resposta = client.post("/espacos/", json=payload_espaco())

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
def test_criar_espaco_rejeita_perfil_sem_permissao(client, headers, perfil):
    resposta = client.post(
        "/espacos/",
        headers=headers[perfil],
        json=payload_espaco(),
    )

    assert resposta.status_code == 403


@pytest.mark.parametrize("nome", ["", "ab"])
def test_criar_espaco_rejeita_nome_invalido(client, headers, nome):
    resposta = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_espaco(nome=nome),
    )

    assert resposta.status_code == 422


def test_criar_espaco_rejeita_nome_duplicado(client, headers, espaco):
    resposta = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_espaco(nome=espaco["nome"]),
    )

    assert resposta.status_code == 409
