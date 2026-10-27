import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.espacos.conftest import criar_pausa


def test_usuario_autenticado_lista_pausas_do_espaco(
    client, headers, espaco
):
    pausa = criar_pausa(client, headers, espaco["id"])

    resposta = client.get(
        f"/espacos/{espaco['id']}/pausas",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert [item["id"] for item in resposta.json()] == [pausa["id"]]


def test_listar_pausas_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.get(f"/espacos/{espaco['id']}/pausas")

    assert resposta.status_code == 401


def test_listar_pausas_de_espaco_inexistente_retorna_nao_encontrado(
    client, headers
):
    resposta = client.get(
        "/espacos/99999/pausas",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404
