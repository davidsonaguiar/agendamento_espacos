import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def payload_espaco(nome="Espaço de teste", **overrides):
    return {
        "nome": nome,
        "descricao": "Espaço para testes de endpoints",
        "capacidade": 12,
        "bloco": "A",
    } | overrides


def criar_espaco(client, headers, nome="Espaço de teste", **overrides):
    resposta = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_espaco(nome, **overrides),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def payload_recurso(nome="Recurso de teste", **overrides):
    return {
        "nome": nome,
        "tipo": "Equipamento",
        "autorizacao_necessaria": False,
        "reserva_independente": True,
    } | overrides


def criar_recurso(
    client,
    headers,
    id_espaco,
    nome="Recurso de teste",
    perfil=PerfilUsuario.ADMINISTRADOR,
    **overrides,
):
    resposta = client.post(
        f"/espacos/{id_espaco}/recursos",
        headers=headers[perfil],
        json=payload_recurso(nome, **overrides),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def payload_pausa(**overrides):
    return {
        "data_inicio": "2027-01-10",
        "data_fim": "2027-01-12",
        "motivo": "Manutenção preventiva",
    } | overrides


def criar_pausa(client, headers, id_espaco, perfil=PerfilUsuario.COORDENADOR):
    resposta = client.post(
        f"/espacos/{id_espaco}/pausas",
        headers=headers[perfil],
        json=payload_pausa(),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.fixture
def espaco(client, headers):
    return criar_espaco(client, headers)


@pytest.fixture
def espaco_inativo(client, headers):
    return criar_espaco(
        client,
        headers,
        nome="Espaço inativo",
        disponibilidade=False,
    )


@pytest.fixture
def recurso(client, headers, espaco):
    return criar_recurso(client, headers, espaco["id"])


@pytest.fixture
def pausa(client, headers, espaco):
    return criar_pausa(client, headers, espaco["id"])
