from datetime import date, time, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.modulos.agendamento.infra.modelos import ReservaAgendaModelo
from app.modulos.espacos.infra.modelos import EspacoHorarioFuncionamentoModelo
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao, payload_solicitacao
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


def horario_futuro() -> dict[str, str]:
    data = date.today() + timedelta(days=14)
    return {
        "data_reserva": data.isoformat(),
        "hora_inicio": "10:00",
        "hora_fim": "11:00",
    }


def criar_recurso(client, headers, id_espaco, *, independente=True):
    resposta = client.post(
        f"/espacos/{id_espaco}/recursos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_recurso(reserva_independente=independente),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def solicitar_recurso(client, headers, id_recurso, *, data=None):
    payload = payload_solicitacao(1)
    payload.pop("id_espaco")
    payload["ids_recursos"] = [id_recurso]
    payload["horarios"] = [data or horario_futuro()]
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.MEMBRO],
        json=payload,
    )
    return resposta


def aprovar(client, headers, solicitacao):
    return client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "status": "Aprovado",
            "justificativa": "Horário validado para o teste.",
        },
    )


def test_solicitacao_e_aprovacao_de_recurso_independente(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso = criar_recurso(client, headers, espaco["id"])

    solicitacao = solicitar_recurso(client, headers, recurso["id"])

    assert solicitacao.status_code == 201, solicitacao.text
    corpo = solicitacao.json()
    assert corpo["id_espaco"] == espaco["id"]
    assert corpo["espaco_reservado"] is False
    assert corpo["ids_recursos"] == [recurso["id"]]

    resposta_aprovacao = aprovar(client, headers, corpo)

    assert resposta_aprovacao.status_code == 200, resposta_aprovacao.text
    assert resposta_aprovacao.json()["status"] == "Aprovado"
    with test_session_factory() as db:
        reserva = db.query(ReservaAgendaModelo).filter_by(
            id_solicitacao=corpo["id"]
        ).one()
        assert reserva.id_espaco == espaco["id"]
        assert reserva.espaco_reservado is False
        assert [item.id for item in reserva.recursos] == [recurso["id"]]


def test_recurso_sem_reserva_independente_nao_pode_ser_solicitado_sozinho(
    client, headers, espaco
):
    recurso = criar_recurso(
        client,
        headers,
        espaco["id"],
        independente=False,
    )

    resposta = solicitar_recurso(client, headers, recurso["id"])

    assert resposta.status_code == 422


def test_solicitacao_exige_espaco_ou_recurso(client, headers, espaco):
    payload = payload_solicitacao(espaco["id"])
    payload.pop("id_espaco")

    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.MEMBRO],
        json=payload,
    )

    assert resposta.status_code == 422


def test_solicitacao_pode_reservar_espaco_com_recurso(
    client, headers, espaco
):
    recurso = criar_recurso(
        client,
        headers,
        espaco["id"],
        independente=False,
    )
    payload = payload_solicitacao(
        espaco["id"],
        ids_recursos=[recurso["id"]],
    )

    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.MEMBRO],
        json=payload,
    )

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["espaco_reservado"] is True
    assert resposta.json()["ids_recursos"] == [recurso["id"]]


def test_reserva_integral_do_espaco_bloqueia_recurso_independente(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso = criar_recurso(client, headers, espaco["id"])
    horario = horario_futuro()
    solicitacao_espaco = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        horarios=[horario],
    )
    aprovada_espaco = aprovar(client, headers, solicitacao_espaco)
    assert aprovada_espaco.status_code == 200, aprovada_espaco.text

    solicitacao_recurso = solicitar_recurso(
        client,
        headers,
        recurso["id"],
        data=horario,
    )
    assert solicitacao_recurso.status_code == 201, solicitacao_recurso.text

    resposta = aprovar(client, headers, solicitacao_recurso.json())

    assert resposta.status_code == 409


def test_reserva_independente_bloqueia_reserva_integral_do_espaco(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso = criar_recurso(client, headers, espaco["id"])
    horario = horario_futuro()
    solicitacao_recurso = solicitar_recurso(
        client,
        headers,
        recurso["id"],
        data=horario,
    )
    assert solicitacao_recurso.status_code == 201, solicitacao_recurso.text
    aprovada_recurso = aprovar(client, headers, solicitacao_recurso.json())
    assert aprovada_recurso.status_code == 200, aprovada_recurso.text

    solicitacao_espaco = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        horarios=[horario],
    )
    resposta = aprovar(client, headers, solicitacao_espaco)

    assert resposta.status_code == 409


def test_recursos_independentes_distintos_podem_ser_reservados_no_mesmo_horario(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    primeiro = criar_recurso(client, headers, espaco["id"])
    segundo = criar_recurso(client, headers, espaco["id"])
    horario = horario_futuro()

    solicitacao_primeiro = solicitar_recurso(
        client,
        headers,
        primeiro["id"],
        data=horario,
    )
    solicitacao_segundo = solicitar_recurso(
        client,
        headers,
        segundo["id"],
        data=horario,
    )
    assert solicitacao_primeiro.status_code == 201, solicitacao_primeiro.text
    assert solicitacao_segundo.status_code == 201, solicitacao_segundo.text

    primeira_aprovacao = aprovar(
        client, headers, solicitacao_primeiro.json()
    )
    segunda_aprovacao = aprovar(
        client, headers, solicitacao_segundo.json()
    )

    assert primeira_aprovacao.status_code == 200, primeira_aprovacao.text
    assert segunda_aprovacao.status_code == 200, segunda_aprovacao.text


def test_reservas_independentes_do_mesmo_recurso_conflitam(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso = criar_recurso(client, headers, espaco["id"])
    horario = horario_futuro()
    primeira = solicitar_recurso(
        client, headers, recurso["id"], data=horario
    )
    segunda = solicitar_recurso(
        client, headers, recurso["id"], data=horario
    )
    assert primeira.status_code == 201, primeira.text
    assert segunda.status_code == 201, segunda.text

    primeira_aprovacao = aprovar(client, headers, primeira.json())
    segunda_aprovacao = aprovar(client, headers, segunda.json())

    assert primeira_aprovacao.status_code == 200, primeira_aprovacao.text
    assert segunda_aprovacao.status_code == 409


def test_disponibilidade_de_recurso_independente_considera_reserva_do_recurso(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso = criar_recurso(client, headers, espaco["id"])
    horario = horario_futuro()
    solicitacao = solicitar_recurso(
        client,
        headers,
        recurso["id"],
        data=horario,
    )
    assert solicitacao.status_code == 201, solicitacao.text
    aprovada = aprovar(client, headers, solicitacao.json())
    assert aprovada.status_code == 200, aprovada.text

    disponibilidade = client.get(
        "/agendamentos/disponibilidade",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "ids_recursos": recurso["id"],
            "data_hora_inicio": (
                f"{horario['data_reserva']}T{horario['hora_inicio']}:00"
            ),
            "data_hora_fim": (
                f"{horario['data_reserva']}T{horario['hora_fim']}:00"
            ),
        },
    )
    horarios = client.get(
        "/agendamentos/horarios-disponiveis",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "ids_recursos": recurso["id"],
            "data_inicio": horario["data_reserva"],
            "data_fim": horario["data_reserva"],
        },
    )

    assert disponibilidade.status_code == 200, disponibilidade.text
    assert disponibilidade.json()["espaco_reservado"] is False
    assert disponibilidade.json()["disponivel"] is False
    assert horarios.status_code == 200, horarios.text
    assert not any(
        item["data_hora_inicio"].endswith("10:00:00")
        for item in horarios.json()
    )


def test_listar_reservas_indica_que_recurso_nao_reserva_o_espaco(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso = criar_recurso(client, headers, espaco["id"])
    horario = horario_futuro()
    solicitacao = solicitar_recurso(
        client,
        headers,
        recurso["id"],
        data=horario,
    )
    assert solicitacao.status_code == 201, solicitacao.text
    aprovada = aprovar(client, headers, solicitacao.json())
    assert aprovada.status_code == 200, aprovada.text

    resposta = client.get(
        "/agendamentos/",
        headers=headers[PerfilUsuario.MEMBRO],
        params={
            "data_hora_inicio": f"{horario['data_reserva']}T00:00:00",
            "data_hora_fim": (
                f"{(date.fromisoformat(horario['data_reserva']) + timedelta(days=1))}"
                "T00:00:00"
            ),
            "id_recurso": recurso["id"],
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["id_espaco"] == espaco["id"]
    assert resposta.json()[0]["espaco_reservado"] is False


def test_replanejar_reserva_independente_preserva_alvo_ao_aceitar(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso_original = criar_recurso(client, headers, espaco["id"])
    recurso_proposto = criar_recurso(client, headers, espaco["id"])
    solicitacao = solicitar_recurso(
        client,
        headers,
        recurso_original["id"],
    )
    assert solicitacao.status_code == 201, solicitacao.text
    data = date.today() + timedelta(days=15)
    proposta = client.post(
        f"/solicitacoes/{solicitacao.json()['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "mensagem": "Proposta para outro recurso disponível.",
            "horarios": [
                {
                    "data_reserva": data.isoformat(),
                    "hora_inicio": "11:00",
                    "hora_fim": "12:00",
                }
            ],
            "ids_recursos": [recurso_proposto["id"]],
        },
    )
    assert proposta.status_code == 200, proposta.text
    id_interacao = proposta.json()["interacoes"][-1]["id"]

    resposta = client.post(
        f"/solicitacoes/{solicitacao.json()['id']}/propostas-replanejamento/"
        f"{id_interacao}/resposta",
        headers=headers[PerfilUsuario.MEMBRO],
        json={"aceita": True, "mensagem": "Aceito o recurso e horário."},
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "Aprovado"
    assert resposta.json()["espaco_reservado"] is False
    assert resposta.json()["ids_recursos"] == [recurso_proposto["id"]]
    with test_session_factory() as db:
        reserva = db.query(ReservaAgendaModelo).filter_by(
            id_solicitacao=solicitacao.json()["id"]
        ).one()
        assert reserva.espaco_reservado is False
        assert [item.id for item in reserva.recursos] == [
            recurso_proposto["id"]
        ]


def test_replanejamento_independente_rejeita_recurso_nao_independente(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso_independente = criar_recurso(client, headers, espaco["id"])
    recurso_comum = criar_recurso(
        client,
        headers,
        espaco["id"],
        independente=False,
    )
    solicitacao = solicitar_recurso(
        client,
        headers,
        recurso_independente["id"],
    )

    resposta = client.post(
        f"/solicitacoes/{solicitacao.json()['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "mensagem": "Proposta com recurso comum.",
            "horarios": [
                {
                    "data_reserva": (
                        date.today() + timedelta(days=15)
                    ).isoformat(),
                    "hora_inicio": "11:00",
                    "hora_fim": "12:00",
                }
            ],
            "ids_recursos": [recurso_comum["id"]],
        },
    )

    assert resposta.status_code == 422
