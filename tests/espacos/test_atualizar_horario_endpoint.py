import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_coordenador_atualiza_horario_de_funcionamento(
    client, headers, espaco
):
    resposta = client.patch(
        f"/espacos/{espaco['id']}/horarios",
        headers=headers[PerfilUsuario.COORDENADOR],
        json={
            "dia_semana": 1,
            "hora_abertura": "09:00",
            "hora_fechamento": "17:00",
            "ativo": True,
        },
    )

    assert resposta.status_code == 200


def test_atualizar_horario_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.patch(
        f"/espacos/{espaco['id']}/horarios",
        json={
            "dia_semana": 1,
            "hora_abertura": "09:00",
            "hora_fechamento": "17:00",
            "ativo": True,
        },
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_atualizar_horario_rejeita_perfil_sem_permissao(
    client, headers, espaco, perfil
):
    resposta = client.patch(
        f"/espacos/{espaco['id']}/horarios",
        headers=headers[perfil],
        json={
            "dia_semana": 1,
            "hora_abertura": "09:00",
            "hora_fechamento": "17:00",
            "ativo": True,
        },
    )

    assert resposta.status_code == 403


def test_atualizar_horario_de_espaco_inexistente_retorna_nao_encontrado(
    client, headers
):
    resposta = client.patch(
        "/espacos/99999/horarios",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "dia_semana": 1,
            "hora_abertura": "09:00",
            "hora_fechamento": "17:00",
            "ativo": True,
        },
    )

    assert resposta.status_code == 404


def test_atualizar_horario_rejeita_dia_semana_invalido(
    client, headers, espaco
):
    resposta = client.patch(
        f"/espacos/{espaco['id']}/horarios",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "dia_semana": 7,
            "hora_abertura": "09:00",
            "hora_fechamento": "17:00",
            "ativo": True,
        },
    )

    assert resposta.status_code == 422
