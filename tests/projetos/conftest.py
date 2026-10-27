import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def payload_projeto(id_responsavel: int, **overrides) -> dict:
    return {
        "descricao": "Projeto de integração",
        "finalidade": "Validar endpoints do projeto",
        "id_responsavel": id_responsavel,
        "quantidade_participantes": 3,
    } | overrides


def criar_projeto(
    client,
    headers,
    id_responsavel: int,
    perfil_criador: PerfilUsuario = PerfilUsuario.ADMINISTRADOR,
    **overrides,
) -> dict:
    resposta = client.post(
        "/projetos/",
        headers=headers[perfil_criador],
        json=payload_projeto(id_responsavel, **overrides),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.fixture
def projeto(client, headers, usuarios):
    return criar_projeto(
        client,
        headers,
        usuarios[PerfilUsuario.SERVIDOR],
        perfil_criador=PerfilUsuario.SERVIDOR,
    )
