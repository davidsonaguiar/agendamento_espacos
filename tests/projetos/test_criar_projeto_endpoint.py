import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.projetos.conftest import payload_projeto


@pytest.mark.parametrize(
    ("perfil_criador", "perfil_responsavel"),
    [
        (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.SERVIDOR),
        (PerfilUsuario.COORDENADOR, PerfilUsuario.SERVIDOR),
        (PerfilUsuario.SERVIDOR, PerfilUsuario.SERVIDOR),
        (PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR),
    ],
)
def test_criar_projeto_com_perfil_permitido(
    client, headers, usuarios, perfil_criador, perfil_responsavel
):
    resposta = client.post(
        "/projetos/",
        headers=headers[perfil_criador],
        json=payload_projeto(usuarios[perfil_responsavel]),
    )

    assert resposta.status_code == 201
    assert resposta.json()["id_responsavel"] == usuarios[perfil_responsavel]
    assert resposta.json()["id_criador"] == usuarios[perfil_criador]


def test_criar_projeto_rejeita_requisicao_sem_token(client, usuarios):
    resposta = client.post(
        "/projetos/",
        json=payload_projeto(usuarios[PerfilUsuario.SERVIDOR]),
    )

    assert resposta.status_code == 401


def test_criar_projeto_rejeita_perfil_aluno(client, headers, usuarios):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.ALUNO],
        json=payload_projeto(usuarios[PerfilUsuario.SERVIDOR]),
    )

    assert resposta.status_code == 403


def test_criar_projeto_rejeita_responsavel_inexistente(client, headers):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_projeto(99999),
    )

    assert resposta.status_code == 404


def test_criar_projeto_rejeita_responsavel_incompativel_com_perfil(
    client, headers, usuarios
):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_projeto(usuarios[PerfilUsuario.COORDENADOR]),
    )

    assert resposta.status_code == 403


def test_criar_projeto_rejeita_campos_invalidos(client, headers, usuarios):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_projeto(
            usuarios[PerfilUsuario.SERVIDOR],
            descricao="x",
            quantidade_participantes=-1,
        ),
    )

    assert resposta.status_code == 422
