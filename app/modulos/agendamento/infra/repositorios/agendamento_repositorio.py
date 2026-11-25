from datetime import datetime

from sqlalchemy.orm import Session

from app.compartilhado.dominio.erros import (
    EntidadeNaoEncontradaErro,
    RegraDeNegocioErro,
)
from app.modulos.agendamento.dominio.contratos import (
    AgendamentoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import PeriodoReserva, ReservaAgenda
from app.modulos.agendamento.infra.modelos import (
    agenda_reserva_recurso_tabela,
    ReservaAgendaModelo,
)
from app.modulos.espacos.infra.modelos import EspacoModelo, RecursoModelo


class AgendamentoRepositorio(AgendamentoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def validar_recursos(
        self,
        id_espaco: int,
        ids_recursos: list[int],
        exigir_independentes: bool = False,
    ) -> None:
        if not ids_recursos:
            return
        recursos = (
            self.db.query(RecursoModelo)
            .filter(
                RecursoModelo.id.in_(ids_recursos),
                RecursoModelo.id_espaco == id_espaco,
            )
            .all()
        )
        ids_encontrados = {recurso.id for recurso in recursos}
        if len(ids_encontrados) != len(set(ids_recursos)):
            id_invalido = next(
                id_recurso
                for id_recurso in ids_recursos
                if id_recurso not in ids_encontrados
            )
            raise EntidadeNaoEncontradaErro("Recurso do espaço", id_invalido)
        recurso_indisponivel = next(
            (recurso for recurso in recursos if not recurso.disponibilidade),
            None,
        )
        if recurso_indisponivel is not None:
            raise RegraDeNegocioErro(
                f"O recurso {recurso_indisponivel.id} está indisponível."
            )
        if exigir_independentes:
            recurso_nao_independente = next(
                (recurso for recurso in recursos if not recurso.reserva_independente),
                None,
            )
            if recurso_nao_independente is not None:
                raise RegraDeNegocioErro(
                    f"O recurso {recurso_nao_independente.id} não pode ser "
                    "reservado independentemente."
                )

    def buscar_id_espaco_dos_recursos(
        self, ids_recursos: list[int]
    ) -> int:
        if not ids_recursos:
            raise RegraDeNegocioErro(
                "Informe ao menos um recurso para reservar independentemente."
            )
        if len(ids_recursos) != len(set(ids_recursos)):
            raise RegraDeNegocioErro("Não informe recursos duplicados.")

        recursos = (
            self.db.query(RecursoModelo)
            .filter(RecursoModelo.id.in_(ids_recursos))
            .all()
        )
        ids_encontrados = {recurso.id for recurso in recursos}
        if len(ids_encontrados) != len(ids_recursos):
            id_invalido = next(
                id_recurso
                for id_recurso in ids_recursos
                if id_recurso not in ids_encontrados
            )
            raise EntidadeNaoEncontradaErro("Recurso", id_invalido)
        if len({recurso.id_espaco for recurso in recursos}) != 1:
            raise RegraDeNegocioErro(
                "Os recursos de uma solicitação devem pertencer ao mesmo espaço."
            )
        id_espaco = recursos[0].id_espaco
        self.validar_recursos(
            id_espaco,
            ids_recursos,
            exigir_independentes=True,
        )
        return id_espaco

    def possui_conflito(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        bloquear_espaco: bool = True,
        ids_recursos: list[int] | None = None,
    ) -> bool:
        ids_recursos = ids_recursos or []
        consulta_espaco = (
            self.db.query(EspacoModelo)
            .filter(EspacoModelo.id == id_espaco)
            .with_for_update()
        )
        if consulta_espaco.first() is None:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)

        self.validar_recursos(
            id_espaco,
            ids_recursos,
            exigir_independentes=not bloquear_espaco,
        )

        conflito_espaco = (
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
        if conflito_espaco and bloquear_espaco:
            return True
        if not bloquear_espaco:
            conflito_reserva_espaco = (
                self.db.query(ReservaAgendaModelo.id)
                .filter(
                    ReservaAgendaModelo.id_espaco == id_espaco,
                    ReservaAgendaModelo.espaco_reservado.is_(True),
                    ReservaAgendaModelo.situacao == "Confirmada",
                    ReservaAgendaModelo.data_hora_inicio < data_hora_fim,
                    ReservaAgendaModelo.data_hora_fim > data_hora_inicio,
                )
                .first()
                is not None
            )
            if conflito_reserva_espaco:
                return True
        if not ids_recursos:
            return False
        return (
            self.db.query(agenda_reserva_recurso_tabela.c.id_agenda)
            .join(
                ReservaAgendaModelo,
                ReservaAgendaModelo.id
                == agenda_reserva_recurso_tabela.c.id_agenda,
            )
            .filter(
                agenda_reserva_recurso_tabela.c.id_recurso.in_(ids_recursos),
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
        ids_recursos: list[int] | None = None,
        espaco_reservado: bool = True,
    ) -> list[ReservaAgenda]:
        ids_recursos = ids_recursos or []
        self.validar_recursos(
            id_espaco,
            ids_recursos,
            exigir_independentes=not espaco_reservado,
        )
        recursos = (
            self.db.query(RecursoModelo)
            .filter(RecursoModelo.id.in_(ids_recursos))
            .all()
            if ids_recursos
            else []
        )
        modelos = [
            ReservaAgendaModelo(
                data_hora_inicio=periodo.data_hora_inicio,
                data_hora_fim=periodo.data_hora_fim,
                situacao="Confirmada",
                id_solicitacao=id_solicitacao,
                id_espaco=id_espaco,
                espaco_reservado=espaco_reservado,
                recursos=recursos,
            )
            for periodo in periodos
        ]
        self.db.add_all(modelos)
        self.db.flush()
        return [
            ReservaAgenda(
                id=modelo.id,
                data_hora_inicio=modelo.data_hora_inicio,
                data_hora_fim=modelo.data_hora_fim,
                situacao=modelo.situacao,
                id_solicitacao=modelo.id_solicitacao,
                id_espaco=modelo.id_espaco,
                espaco_reservado=modelo.espaco_reservado,
                ids_recursos=[recurso.id for recurso in recursos],
            )
            for modelo in modelos
        ]


    def listar(
        self,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        id_espaco: int | None = None,
        id_recurso: int | None = None,
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
        if id_recurso is not None:
            consulta = consulta.filter(
                ReservaAgendaModelo.recursos.any(
                    RecursoModelo.id == id_recurso
                )
            )
        modelos = consulta.order_by(ReservaAgendaModelo.data_hora_inicio).all()
        return [
            ReservaAgenda(
                id=modelo.id,
                data_hora_inicio=modelo.data_hora_inicio,
                data_hora_fim=modelo.data_hora_fim,
                situacao=modelo.situacao,
                id_solicitacao=modelo.id_solicitacao,
                id_espaco=modelo.id_espaco,
                espaco_reservado=modelo.espaco_reservado,
                ids_recursos=[recurso.id for recurso in modelo.recursos],
            )
            for modelo in modelos
        ]
