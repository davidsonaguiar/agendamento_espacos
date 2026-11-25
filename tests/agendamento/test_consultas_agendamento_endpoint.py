from datetime import date, time, timedelta

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.modulos.espacos.infra.modelos import EspacoHorarioFuncionamentoModelo
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao
from tests.espacos.conftest import payload_recurso


def configurar_horarios(
    test_session_factory: sessionmaker[Session], id_espaco: int
) -> None:
    with test_session_factory() as db:
        db.add_all(
            [
                EspacoHorarioFuncionamentoModelo(
                    id_espaco=id_espaco,
                    dia_semana=dia_semana,
                    hora_abertura=time(8),
                    hora_fechamento=time(17),
                    ativo=True,
                )
                for dia_semana in range(7)
            ]
        )
        db.commit()


def data_futura() -> date:
    return date.today() + timedelta(days=14)


def payload_horario(data: date, inicio: str = "10:00", fim: str = "11:00"):
    return {
        "data_reserva": data.isoformat(),
        "hora_inicio": inicio,
        "hora_fim": fim,
    }


def test_consultar_disponibilidade_retorna_disponivel(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    data = data_futura()

    resposta = client.get(
        "/agendamentos/disponibilidade",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "id_espaco": espaco["id"],
            "data_hora_inicio": f"{data.isoformat()}T10:00:00",
            "data_hora_fim": f"{data.isoformat()}T11:00:00",
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["disponivel"] is True
    assert resposta.json()["motivo"] is None


def test_consultar_disponibilidade_informa_conflito_de_reserva(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    data = data_futura()
    solicitacao = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        horarios=[payload_horario(data)],
    )
    aprovada = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"status": "Aprovado", "justificativa": "Reserva confirmada."},
    )
    assert aprovada.status_code == 200, aprovada.text

    resposta = client.get(
        "/agendamentos/disponibilidade",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "id_espaco": espaco["id"],
            "data_hora_inicio": f"{data.isoformat()}T10:00:00",
            "data_hora_fim": f"{data.isoformat()}T11:00:00",
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["disponivel"] is False
    assert "conflita" in resposta.json()["motivo"]


@pytest.mark.parametrize(
    "inicio,fim",
    [
        ("2030-01-02T11:00:00", "2030-01-02T10:00:00"),
        ("2030-01-02T10:00:00+00:00", "2030-01-02T11:00:00+00:00"),
    ],
)
def test_consultar_disponibilidade_rejeita_periodo_invalido(
    client, headers, espaco, inicio, fim
):
    resposta = client.get(
        "/agendamentos/disponibilidade",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "id_espaco": espaco["id"],
            "data_hora_inicio": inicio,
            "data_hora_fim": fim,
        },
    )

    assert resposta.status_code == 422


def test_consultar_disponibilidade_rejeita_requisicao_sem_token(
    client, espaco
):
    resposta = client.get(
        "/agendamentos/disponibilidade",
        params={
            "id_espaco": espaco["id"],
            "data_hora_inicio": "2030-01-02T10:00:00",
            "data_hora_fim": "2030-01-02T11:00:00",
        },
    )

    assert resposta.status_code == 401


def test_listar_reservas_retorna_reserva_no_periodo(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    data = data_futura()
    solicitacao = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        horarios=[payload_horario(data)],
    )
    aprovada = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"status": "Aprovado", "justificativa": "Reserva confirmada."},
    )
    assert aprovada.status_code == 200, aprovada.text

    resposta = client.get(
        "/agendamentos/",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "data_hora_inicio": f"{data.isoformat()}T00:00:00",
            "data_hora_fim": f"{(data + timedelta(days=1)).isoformat()}T00:00:00",
            "id_espaco": espaco["id"],
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["id_solicitacao"] == solicitacao["id"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "data_hora_inicio": "2030-01-02T11:00:00",
            "data_hora_fim": "2030-01-02T10:00:00",
        },
        {
            "data_hora_inicio": "2030-01-02T10:00:00+00:00",
            "data_hora_fim": "2030-01-02T11:00:00+00:00",
        },
        {
            "data_hora_inicio": "2030-01-02T10:00:00",
            "data_hora_fim": "2030-01-02T11:00:00",
            "id_espaco": 0,
        },
    ],
)
def test_listar_reservas_rejeita_filtros_invalidos(client, headers, params):
    resposta = client.get(
        "/agendamentos/",
        headers=headers[PerfilUsuario.MEMBRO],
        params=params,
    )

    assert resposta.status_code == 422


def test_listar_reservas_rejeita_requisicao_sem_token(client):
    resposta = client.get(
        "/agendamentos/",
        params={
            "data_hora_inicio": "2030-01-02T10:00:00",
            "data_hora_fim": "2030-01-02T11:00:00",
        },
    )

    assert resposta.status_code == 401


def test_consultar_horarios_disponiveis_rejeita_intervalo_invertido(
    client, headers, espaco
):
    data = data_futura()

    resposta = client.get(
        "/agendamentos/horarios-disponiveis",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "id_espaco": espaco["id"],
            "data_inicio": (data + timedelta(days=1)).isoformat(),
            "data_fim": data.isoformat(),
        },
    )

    assert resposta.status_code == 422


def test_consultar_horarios_disponiveis_rejeita_periodo_acima_do_limite(
    client, headers, espaco
):
    data = data_futura()

    resposta = client.get(
        "/agendamentos/horarios-disponiveis",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "id_espaco": espaco["id"],
            "data_inicio": data.isoformat(),
            "data_fim": (data + timedelta(days=31)).isoformat(),
        },
    )

    assert resposta.status_code == 422


def test_consultar_horarios_disponiveis_rejeita_recursos_duplicados(
    client, headers, espaco
):
    recurso = client.post(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_recurso(),
    )
    assert recurso.status_code == 201, recurso.text
    id_recurso = recurso.json()["id"]
    data = data_futura()

    resposta = client.get(
        "/agendamentos/horarios-disponiveis",
        headers=headers[PerfilUsuario.MEMBRO],
        params=[
            ("id_espaco", espaco["id"]),
            ("data_inicio", data.isoformat()),
            ("data_fim", data.isoformat()),
            ("ids_recursos", id_recurso),
            ("ids_recursos", id_recurso),
        ],
    )

    assert resposta.status_code == 422


def test_consultar_horarios_disponiveis_rejeita_requisicao_sem_token(
    client, espaco
):
    data = data_futura()
    resposta = client.get(
        "/agendamentos/horarios-disponiveis",
        params={
            "id_espaco": espaco["id"],
            "data_inicio": data.isoformat(),
            "data_fim": data.isoformat(),
        },
    )

    assert resposta.status_code == 401
