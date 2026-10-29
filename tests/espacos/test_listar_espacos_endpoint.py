import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.espacos.conftest import criar_espaco


def test_administrador_lista_espacos_ativos_e_inativos(
    client, headers, espaco, espaco_inativo
):
    resposta = client.get(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    ids = {item["id"] for item in resposta.json()}
    assert {espaco["id"], espaco_inativo["id"]} <= ids


def test_servidor_lista_somente_espacos_ativos(
    client, headers, espaco, espaco_inativo
):
    resposta = client.get(
        "/espacos/",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    ids = {item["id"] for item in resposta.json()}
    assert espaco["id"] in ids
    assert espaco_inativo["id"] not in ids


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.COORDENADOR, PerfilUsuario.MONITOR],
)
def test_usuario_vinculado_lista_espacos(
    client, headers, usuarios, perfil
):
    espaco = criar_espaco(client, headers)
    vincular = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[perfil]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )
    assert vincular.status_code == 201

    resposta = client.get(
        "/espacos/",
        headers=headers[perfil],
    )

    assert resposta.status_code == 200
    assert espaco["id"] in {item["id"] for item in resposta.json()}


def test_listar_espacos_rejeita_requisicao_sem_token(client):
    resposta = client.get("/espacos/")

    assert resposta.status_code == 401


def test_listar_espacos_aplica_paginacao(client, headers):
    criados = [criar_espaco(client, headers, nome=f"Espaço paginado {i}") for i in range(3)]

    resposta = client.get(
        "/espacos/?skip=1&limit=1",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["id"] in {espaco["id"] for espaco in criados}


@pytest.mark.parametrize("query", ["skip=-1", "limit=0", "limit=101"])
def test_listar_espacos_rejeita_paginacao_invalida(client, headers, query):
    resposta = client.get(
        f"/espacos/?{query}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 422
