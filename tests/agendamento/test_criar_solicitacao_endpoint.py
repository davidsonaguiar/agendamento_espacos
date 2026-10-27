from datetime import date, timedelta

import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import (
    criar_projeto,
    criar_solicitacao,
    payload_solicitacao,
)


def test_servidor_cria_solicitacao_com_sucesso(client, headers, espaco, usuarios):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(
            espaco["id"],
            ids_usuarios_envolvidos=[usuarios[PerfilUsuario.MONITOR]],
        ),
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "Pendente"
    assert corpo["id_solicitante"] == usuarios[PerfilUsuario.SERVIDOR]
    assert len(corpo["horarios"]) == 1
    assert corpo["usuarios_envolvidos"][0]["id_usuario"] == usuarios[PerfilUsuario.MONITOR]


def test_servidor_cria_solicitacao_associada_a_projeto(
    client, headers, espaco, projeto
):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(espaco["id"], id_projeto=projeto["id"]),
    )

    assert resposta.status_code == 201
    assert resposta.json()["id_projeto"] == projeto["id"]


def test_criar_solicitacao_rejeita_perfil_diferente_de_servidor(
    client, headers, espaco
):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.MONITOR],
        json=payload_solicitacao(espaco["id"]),
    )

    assert resposta.status_code == 403


def test_criar_solicitacao_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.post(
        "/solicitacoes/",
        json=payload_solicitacao(espaco["id"]),
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "alteracoes",
    [
        {"tipo": "Tipo inexistente"},
        {"finalidade": "x"},
        {"id_espaco": 0},
        {"horarios": []},
        {"horarios": [{"data_reserva": "2000-01-01", "hora_inicio": "10:00", "hora_fim": "12:00"}]},
        {"horarios": [{"data_reserva": (date.today() + timedelta(days=2)).isoformat(), "hora_inicio": "12:00", "hora_fim": "10:00"}]},
        {"campos_extras": True},
    ],
)
def test_criar_solicitacao_rejeita_payload_invalido(
    client, headers, espaco, alteracoes
):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(espaco["id"], **alteracoes),
    )

    assert resposta.status_code == 422


def test_criar_solicitacao_rejeita_espaco_inexistente(client, headers):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(99999),
    )

    assert resposta.status_code == 404


def test_criar_solicitacao_rejeita_projeto_inexistente(client, headers, espaco):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(espaco["id"], id_projeto=99999),
    )

    assert resposta.status_code == 404


def test_criar_solicitacao_rejeita_solicitante_na_lista_de_envolvidos(
    client, headers, espaco, usuarios
):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(
            espaco["id"],
            ids_usuarios_envolvidos=[usuarios[PerfilUsuario.SERVIDOR]],
        ),
    )

    assert resposta.status_code == 422


def test_criar_solicitacao_rejeita_usuario_envolvido_inexistente(
    client, headers, espaco
):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(espaco["id"], ids_usuarios_envolvidos=[99999]),
    )

    assert resposta.status_code == 404


def test_criar_solicitacao_nao_permite_repetir_usuarios_envolvidos(
    client, headers, espaco, usuarios
):
    id_monitor = usuarios[PerfilUsuario.MONITOR]
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json=payload_solicitacao(
            espaco["id"],
            ids_usuarios_envolvidos=[id_monitor, id_monitor],
        ),
    )

    assert resposta.status_code == 422
