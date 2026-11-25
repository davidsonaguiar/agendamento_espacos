from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco
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
        headers=headers[PerfilUsuario.MEMBRO],
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
        headers=headers[PerfilEspaco.COORDENADOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert {uma["id"], outra["id"]} <= ids_retornados


def test_coordenador_nao_lista_solicitacoes_de_outro_espaco(
    client, headers, espaco
):
    resposta_outro_espaco = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"nome": "Outro espaço"},
    )
    assert resposta_outro_espaco.status_code == 201
    outro_espaco = resposta_outro_espaco.json()
    solicitacao_fora_do_escopo = criar_solicitacao(
        client, headers, outro_espaco["id"]
    )

    resposta = client.get(
        "/solicitacoes/",
        headers=headers[PerfilEspaco.COORDENADOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert solicitacao_fora_do_escopo["id"] not in ids_retornados


def test_listar_solicitacoes_rejeita_requisicao_sem_token(client):
    resposta = client.get("/solicitacoes/")

    assert resposta.status_code == 401
