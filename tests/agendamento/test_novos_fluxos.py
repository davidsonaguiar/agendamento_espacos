from datetime import date, time, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.modulos.agendamento.infra.modelos import ReservaAgendaModelo
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


def test_consultar_horarios_disponiveis_considera_reservas(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    data = data_futura()
    solicitacao = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        horarios=[payload_horario(data, "08:00", "09:00")],
    )
    aprovada = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"status": "Aprovado", "justificativa": "Aprovada para teste."},
    )
    assert aprovada.status_code == 200, aprovada.text

    resposta = client.get(
        "/agendamentos/horarios-disponiveis",
        headers=headers[PerfilUsuario.SERVIDOR],
        params={
            "id_espaco": espaco["id"],
            "data_inicio": data.isoformat(),
            "data_fim": data.isoformat(),
        },
    )

    assert resposta.status_code == 200, resposta.text
    horarios = resposta.json()
    assert all(item["data_hora_inicio"].startswith(data.isoformat()) for item in horarios)
    assert not any(item["data_hora_inicio"].endswith("08:00:00") for item in horarios)
    assert any(item["data_hora_inicio"].endswith("09:00:00") for item in horarios)


def test_fluxo_de_complementacao_preserva_historico(
    client, headers, espaco
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])

    pedido = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao",
        headers=headers[PerfilUsuario.COORDENADOR],
        json={"mensagem": "Informe os equipamentos necessários."},
    )
    assert pedido.status_code == 200, pedido.text
    assert pedido.json()["status"] == "AguardandoComplementacao"

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao/resposta",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={"mensagem": "Será utilizado um projetor."},
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "Pendente"
    assert [
        item["tipo"] for item in resposta.json()["interacoes"]
    ] == ["ComplementacaoSolicitada", "ComplementacaoRespondida"]


def test_aceitar_proposta_aprova_e_vincula_recurso(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso_response = client.post(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_recurso(),
    )
    assert recurso_response.status_code == 201, recurso_response.text
    id_recurso = recurso_response.json()["id"]
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    data = data_futura()

    proposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "mensagem": "Horário alternativo disponível.",
            "horarios": [payload_horario(data)],
            "ids_recursos": [id_recurso],
        },
    )
    assert proposta.status_code == 200, proposta.text
    interacao = proposta.json()["interacoes"][-1]
    assert proposta.json()["status"] == "AguardandoRespostaProposta"

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento/"
        f"{interacao['id']}/resposta",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={"aceita": True, "mensagem": "Aceito a nova data."},
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "Aprovado"
    assert resposta.json()["ids_recursos"] == [id_recurso]

    with test_session_factory() as db:
        reserva = db.query(ReservaAgendaModelo).filter_by(
            id_solicitacao=solicitacao["id"]
        ).one()
        assert [item.id for item in reserva.recursos] == [id_recurso]

    reservas = client.get(
        "/agendamentos/",
        headers=headers[PerfilUsuario.SERVIDOR],
        params={
            "data_hora_inicio": f"{data.isoformat()}T00:00:00",
            "data_hora_fim": f"{(data + timedelta(days=1)).isoformat()}T00:00:00",
            "id_recurso": id_recurso,
        },
    )
    assert reservas.status_code == 200, reservas.text
    assert len(reservas.json()) == 1
    assert reservas.json()[0]["ids_recursos"] == [id_recurso]


def test_recusar_proposta_retorna_solicitacao_a_pendente(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    proposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "mensagem": "Proposta de horário.",
            "horarios": [payload_horario(data_futura())],
            "ids_recursos": [],
        },
    )
    assert proposta.status_code == 200, proposta.text
    interacao = proposta.json()["interacoes"][-1]

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento/"
        f"{interacao['id']}/resposta",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={"aceita": False, "mensagem": "Esse horário não funciona."},
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "Pendente"
    assert resposta.json()["interacoes"][-2]["situacao"] == "Recusada"
