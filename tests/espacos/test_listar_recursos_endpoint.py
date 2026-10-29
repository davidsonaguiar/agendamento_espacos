import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.espacos.conftest import criar_recurso


@pytest.mark.parametrize(
    "perfil",
    [
        PerfilUsuario.ADMINISTRADOR,
        PerfilUsuario.COORDENADOR,
        PerfilUsuario.MONITOR,
    ],
)
def test_perfis_autorizados_veem_recursos_indisponiveis(
    client, headers, espaco, perfil
):
    recurso = criar_recurso(
        client,
        headers,
        espaco["id"],
        nome="Recurso a indisponibilizar",
    )
    removido = client.delete(
        f"/espacos/{espaco['id']}/recursos/{recurso['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )
    resposta = client.get(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[perfil],
    )

    assert removido.status_code == 200
    assert resposta.status_code == 200
    assert any(item["id"] == recurso["id"] for item in resposta.json())


def test_servidor_lista_somente_recursos_disponiveis(
    client, headers, espaco
):
    disponivel = criar_recurso(
        client, headers, espaco["id"], nome="Recurso disponível"
    )
    indisponivel = criar_recurso(
        client, headers, espaco["id"], nome="Recurso indisponível"
    )
    client.delete(
        f"/espacos/{espaco['id']}/recursos/{indisponivel['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    resposta = client.get(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    ids = {item["id"] for item in resposta.json()}
    assert disponivel["id"] in ids
    assert indisponivel["id"] not in ids


def test_listar_recursos_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.get(f"/espacos/{espaco['id']}/recursos")

    assert resposta.status_code == 401


def test_listar_recursos_de_espaco_inexistente_retorna_nao_encontrado(
    client, headers
):
    resposta = client.get(
        "/espacos/99999/recursos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_listar_recursos_aplica_paginacao(client, headers, espaco):
    recursos = [
        criar_recurso(
            client,
            headers,
            espaco["id"],
            nome=f"Recurso paginado {i}",
        )
        for i in range(3)
    ]

    resposta = client.get(
        f"/espacos/{espaco['id']}/recursos?skip=1&limit=1",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["id"] in {recurso["id"] for recurso in recursos}


@pytest.mark.parametrize(
    "query", ["skip=-1", "limit=0", "limit=101"]
)
def test_listar_recursos_rejeita_paginacao_invalida(
    client, headers, espaco, query
):
    resposta = client.get(
        f"/espacos/{espaco['id']}/recursos?{query}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 422
