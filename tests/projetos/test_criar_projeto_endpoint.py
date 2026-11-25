import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from tests.projetos.conftest import payload_projeto


@pytest.mark.parametrize(
    ("perfil_criador", "perfil_responsavel", "status_esperado"),
    [
        (
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.MEMBRO,
            201,
        ),
        (
            PerfilEspaco.COORDENADOR,
            PerfilEspaco.COORDENADOR,
            201,
        ),
        (PerfilUsuario.MEMBRO, PerfilUsuario.MEMBRO, 201),
        (PerfilEspaco.MONITOR, PerfilUsuario.MEMBRO, 403),
    ],
)
def test_criar_projeto_com_perfil_permitido(
    client, headers, usuarios, perfil_criador, perfil_responsavel, status_esperado
):
    resposta = client.post(
        "/projetos/",
        headers=headers[perfil_criador],
        json=payload_projeto(usuarios[perfil_responsavel]),
    )

    assert resposta.status_code == status_esperado
    if status_esperado == 201:
        assert resposta.json()["id_responsavel"] == usuarios[perfil_responsavel]
        assert resposta.json()["id_criador"] == usuarios[perfil_criador]


def test_criar_projeto_rejeita_requisicao_sem_token(client, usuarios):
    resposta = client.post(
        "/projetos/",
        json=payload_projeto(usuarios[PerfilUsuario.MEMBRO]),
    )

    assert resposta.status_code == 401


def test_membro_nao_pode_criar_projeto_para_outro_membro(
    client, headers, usuarios
):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.MEMBRO],
        json=payload_projeto(usuarios[PerfilEspaco.COORDENADOR]),
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
        headers=headers[PerfilUsuario.MEMBRO],
        json=payload_projeto(usuarios[PerfilEspaco.COORDENADOR]),
    )

    assert resposta.status_code == 403


def test_criar_projeto_rejeita_campos_invalidos(client, headers, usuarios):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_projeto(
            usuarios[PerfilUsuario.MEMBRO],
            descricao="x",
            quantidade_participantes=-1,
        ),
    )

    assert resposta.status_code == 422
