from datetime import datetime

from sqlalchemy.orm import Session

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.agendamento.dominio.contratos import (
    AgendamentoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import PeriodoReserva, ReservaAgenda
from app.modulos.agendamento.infra.modelos import ReservaAgendaModelo
from app.modulos.espacos.infra.modelos import EspacoModelo


class AgendamentoRepositorio(AgendamentoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def possui_conflito(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        bloquear_espaco: bool = False,
    ) -> bool:
        consulta_espaco = self.db.query(EspacoModelo).filter(
            EspacoModelo.id == id_espaco
        )
        if bloquear_espaco:
            consulta_espaco = consulta_espaco.with_for_update()
        espaco = consulta_espaco.first()
        if espaco is None:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)

        return (
            self.db.query(ReservaAgendaModelo.id)
            .filter(
                ReservaAgendaModelo.id_espaco == id_espaco,
                ReservaAgendaModelo.situacao == "Confirmada",
                ReservaAgendaModelo.data_hora_inicio < data_hora_fim,
                ReservaAgendaModelo.data_hora_fim > data_hora_inicio,
            )
            .first()
            is not None
        )

    def reservar(
        self,
        id_solicitacao: int,
        id_espaco: int,
        periodos: list[PeriodoReserva],
    ) -> list[ReservaAgenda]:
        modelos = [
            ReservaAgendaModelo(
                data_hora_inicio=periodo.data_hora_inicio,
                data_hora_fim=periodo.data_hora_fim,
                situacao="Confirmada",
                id_solicitacao=id_solicitacao,
                id_espaco=id_espaco,
            )
            for periodo in periodos
        ]
        self.db.add_all(modelos)
        self.db.flush()
        return [ReservaAgenda.model_validate(modelo) for modelo in modelos]

    def listar(
        self,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        id_espaco: int | None = None,
    ) -> list[ReservaAgenda]:
        consulta = self.db.query(ReservaAgendaModelo).filter(
            ReservaAgendaModelo.situacao == "Confirmada",
            ReservaAgendaModelo.data_hora_inicio < data_hora_fim,
            ReservaAgendaModelo.data_hora_fim > data_hora_inicio,
        )
        if id_espaco is not None:
            consulta = consulta.filter(
                ReservaAgendaModelo.id_espaco == id_espaco
            )
        modelos = consulta.order_by(ReservaAgendaModelo.data_hora_inicio).all()
        return [ReservaAgenda.model_validate(modelo) for modelo in modelos]
