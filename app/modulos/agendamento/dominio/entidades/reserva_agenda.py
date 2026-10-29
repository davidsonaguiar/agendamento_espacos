from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, model_validator
from pydantic import Field


class SituacaoReserva(str, Enum):
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"


class PeriodoReserva(BaseModel):
    data_hora_inicio: datetime
    data_hora_fim: datetime

    @model_validator(mode="after")
    def validar_periodo(self) -> "PeriodoReserva":
        if (
            self.data_hora_inicio.tzinfo is not None
            or self.data_hora_fim.tzinfo is not None
        ):
            raise ValueError("Use data e hora locais sem fuso horário.")
        if self.data_hora_inicio >= self.data_hora_fim:
            raise ValueError("O fim deve ser posterior ao início.")
        return self


class ReservaAgenda(PeriodoReserva):
    id: int
    situacao: SituacaoReserva
    id_solicitacao: int
    id_espaco: int
    ids_recursos: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
