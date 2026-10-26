from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol

from app.modulos.agendamento.dominio.entidades import PeriodoReserva, ReservaAgenda


class AgendamentoRepositorioContrato(ABC):
    @abstractmethod
    def possui_conflito(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        bloquear_espaco: bool = False,
    ) -> bool:
        pass

    @abstractmethod
    def reservar(
        self,
        id_solicitacao: int,
        id_espaco: int,
        periodos: list[PeriodoReserva],
    ) -> list[ReservaAgenda]:
        pass

    @abstractmethod
    def listar(
        self,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        id_espaco: int | None = None,
    ) -> list[ReservaAgenda]:
        pass


class RegrasFuncionamentoContrato(Protocol):
    def verificar_funcionamento(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
    ) -> str | None:
        ...
