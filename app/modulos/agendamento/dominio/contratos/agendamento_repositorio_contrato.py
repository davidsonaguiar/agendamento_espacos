from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol

from app.modulos.agendamento.dominio.entidades import PeriodoReserva, ReservaAgenda
from app.modulos.espacos.dominio.entidades import (
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
)


class AgendamentoRepositorioContrato(ABC):
    @abstractmethod
    def validar_recursos(self, id_espaco: int, ids_recursos: list[int]) -> None:
        pass

    @abstractmethod
    def possui_conflito(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        bloquear_espaco: bool = False,
        ids_recursos: list[int] | None = None,
    ) -> bool:
        pass

    @abstractmethod
    def reservar(
        self,
        id_solicitacao: int,
        id_espaco: int,
        periodos: list[PeriodoReserva],
        ids_recursos: list[int] | None = None,
    ) -> list[ReservaAgenda]:
        pass

    @abstractmethod
    def listar(
        self,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        id_espaco: int | None = None,
        id_recurso: int | None = None,
    ) -> list[ReservaAgenda]:
        pass

class RegrasFuncionamentoContrato(Protocol):
    def buscar_horarios_por_espaco(
        self, id_espaco: int
    ) -> list[EspacoHorarioFuncionamento]:
        ...

    def buscar_pausas_por_espaco(
        self, id_espaco: int
    ) -> list[EspacoPausaFuncionamento]:
        ...

    def verificar_funcionamento(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
    ) -> str | None:
        ...
