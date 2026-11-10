from datetime import date, time, timedelta

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.modulos.agendamento.infra.modelos import ReservaAgendaModelo
from app.modulos.espacos.infra.modelos import EspacoHorarioFuncionamentoModelo
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from tests.agendamento.conftest import criar_solicitacao


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


def payload_proposta(data: date, **overrides):
    return {
        "mensagem": "Horário alternativo disponível.",
        "horarios": [payload_horario(data)],
        "ids_recursos": [],
    } | overrides


def propor(client, headers, id_solicitacao, data):
    resposta = client.post(
        f"/solicitacoes/{id_solicitacao}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_proposta(data),
    )
    assert resposta.status_code == 200, resposta.text
    return resposta


def test_administrador_rejeita_solicitacao_com_sucesso(
    client, headers, espaco
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])

    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"status": "Rejeitado", "justificativa": "Solicitação não aprovada."},
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "Rejeitado"


def test_decidir_solicitacao_rejeita_id_inexistente(client, headers):
    resposta = client.patch(
        "/solicitacoes/99999/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"status": "Rejeitado", "justificativa": "Não aprovada."},
    )

    assert resposta.status_code == 404


def test_decidir_solicitacao_nao_permite_decidir_duas_vezes(
    client, headers, espaco
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    url = f"/solicitacoes/{solicitacao['id']}/decisao"
    decisao = {"status": "Rejeitado", "justificativa": "Não aprovada."}

    primeira = client.patch(
        url,
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=decisao,
    )
    segunda = client.patch(
        url,
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=decisao,
    )

    assert primeira.status_code == 200, primeira.text
    assert segunda.status_code == 409


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MEMBRO, PerfilEspaco.MONITOR],
)
def test_decidir_solicitacao_requer_perfil_gestor(
    client, headers, espaco, perfil
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])

    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[perfil],
        json={"status": "Rejeitado", "justificativa": "Não aprovada."},
    )

    assert resposta.status_code == 403


def test_decidir_solicitacao_rejeita_requisicao_sem_token(client, solicitacao):
    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        json={"status": "Rejeitado", "justificativa": "Não aprovada."},
    )

    assert resposta.status_code == 401


def test_aprovacao_em_conflito_nao_cria_reserva_nem_altera_solicitacao(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    horario = [payload_horario(data_futura())]
    primeira = criar_solicitacao(
        client, headers, espaco["id"], horarios=horario
    )
    segunda = criar_solicitacao(
        client, headers, espaco["id"], horarios=horario
    )
    decisao = {
        "status": "Aprovado",
        "justificativa": "Horário aprovado para teste.",
    }

    aprovada = client.patch(
        f"/solicitacoes/{primeira['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=decisao,
    )
    conflito = client.patch(
        f"/solicitacoes/{segunda['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=decisao,
    )

    assert aprovada.status_code == 200, aprovada.text
    assert conflito.status_code == 409
    with test_session_factory() as db:
        assert (
            db.query(ReservaAgendaModelo)
            .filter_by(id_solicitacao=primeira["id"])
            .count()
            == 1
        )
        assert (
            db.query(ReservaAgendaModelo)
            .filter_by(id_solicitacao=segunda["id"])
            .count()
            == 0
        )
    obtida = client.get(
        f"/solicitacoes/{segunda['id']}",
        headers=headers[PerfilUsuario.MEMBRO],
    )
    assert obtida.status_code == 200
    assert obtida.json()["status"] == "Pendente"


def test_solicitar_complementacao_rejeita_solicitacao_inexistente(
    client, headers
):
    resposta = client.post(
        "/solicitacoes/99999/complementacao",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"mensagem": "Informe os equipamentos."},
    )

    assert resposta.status_code == 404


def test_solicitar_complementacao_nao_permite_estado_invalido(
    client, headers, espaco
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    pedido = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"mensagem": "Informe os equipamentos."},
    )
    assert pedido.status_code == 200, pedido.text

    repetido = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"mensagem": "Envie detalhes adicionais."},
    )

    assert repetido.status_code == 409


@pytest.mark.parametrize(
    "mensagem",
    ["", "  "],
)
def test_solicitar_complementacao_rejeita_mensagem_invalida(
    client, headers, espaco, mensagem
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"mensagem": mensagem},
    )

    assert resposta.status_code == 422


def test_solicitar_complementacao_requer_perfil_gestor(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao",
        headers=headers[PerfilUsuario.MEMBRO],
        json={"mensagem": "Informe os equipamentos."},
    )

    assert resposta.status_code == 403


def test_responder_complementacao_rejeita_estado_invalido(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao/resposta",
        headers=headers[PerfilUsuario.MEMBRO],
        json={"mensagem": "Segue informação adicional."},
    )

    assert resposta.status_code == 409


def test_responder_complementacao_rejeita_usuario_diferente(
    client, headers, espaco, outro_servidor
):
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    pedido = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"mensagem": "Informe os equipamentos."},
    )
    assert pedido.status_code == 200, pedido.text

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/complementacao/resposta",
        headers=outro_servidor["headers"],
        json={"mensagem": "Segue informação adicional."},
    )

    assert resposta.status_code == 403


def test_propor_replanejamento_rejeita_solicitacao_inexistente(
    client, headers
):
    resposta = client.post(
        "/solicitacoes/99999/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_proposta(data_futura()),
    )

    assert resposta.status_code == 404


def test_propor_replanejamento_rejeita_periodo_que_nao_tem_uma_hora(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    solicitacao = criar_solicitacao(client, headers, espaco["id"])

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_proposta(
            data_futura(),
            horarios=[payload_horario(data_futura(), "10:00", "12:00")],
        ),
    )

    assert resposta.status_code == 422


def test_propor_replanejamento_nao_permite_segunda_proposta_pendente(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    primeira = propor(client, headers, solicitacao["id"], data_futura())

    segunda = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json=payload_proposta(data_futura() + timedelta(days=1)),
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 409


def test_propor_replanejamento_requer_perfil_gestor(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento",
        headers=headers[PerfilUsuario.MEMBRO],
        json=payload_proposta(data_futura()),
    )

    assert resposta.status_code == 403


def test_responder_proposta_rejeita_proposta_inexistente(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    proposta = propor(client, headers, solicitacao["id"], data_futura())

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento/99999/resposta",
        headers=headers[PerfilUsuario.MEMBRO],
        json={"aceita": False, "mensagem": "Não posso nesse horário."},
    )
    assert resposta.status_code == 404
    assert resposta.status_code == 404


def test_responder_proposta_rejeita_usuario_diferente(
    client, headers, espaco, outro_servidor, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    solicitacao = criar_solicitacao(client, headers, espaco["id"])
    proposta = propor(client, headers, solicitacao["id"], data_futura())
    id_interacao = proposta.json()["interacoes"][-1]["id"]

    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento/"
        f"{id_interacao}/resposta",
        headers=outro_servidor["headers"],
        json={"aceita": False, "mensagem": "Não posso nesse horário."},
    )

    assert resposta.status_code == 403


def test_responder_proposta_rejeita_estado_sem_proposta_pendente(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento/1/resposta",
        headers=headers[PerfilUsuario.MEMBRO],
        json={"aceita": False, "mensagem": "Não posso nesse horário."},
    )

    assert resposta.status_code == 409


def test_responder_proposta_rejeita_requisicao_sem_token(
    client, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/propostas-replanejamento/1/resposta",
        json={"aceita": False, "mensagem": "Não posso nesse horário."},
    )

    assert resposta.status_code == 401
