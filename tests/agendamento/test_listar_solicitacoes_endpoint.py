from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao


def test_solicitante_lista_somente_suas_solicitacoes(
    client, headers, espaco, outro_servidor
):
    propria = criar_solicitacao(client, headers, espaco["id"])
    outra = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        cabecalho=outro_servidor["headers"],
    )

    resposta = client.get(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert propria["id"] in ids_retornados
    assert outra["id"] not in ids_retornados


def test_administrador_lista_todas_as_solicitacoes(
    client, headers, espaco, outro_servidor
):
    uma = criar_solicitacao(client, headers, espaco["id"])
    outra = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        cabecalho=outro_servidor["headers"],
    )

    resposta = client.get(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert {uma["id"], outra["id"]} <= ids_retornados


def test_coordenador_lista_todas_as_solicitacoes(
    client, headers, espaco, outro_servidor
):
    uma = criar_solicitacao(client, headers, espaco["id"])
    outra = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        cabecalho=outro_servidor["headers"],
    )

    resposta = client.get(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert {uma["id"], outra["id"]} <= ids_retornados


def test_listar_solicitacoes_rejeita_requisicao_sem_token(client):
    resposta = client.get("/solicitacoes/")

    assert resposta.status_code == 401
