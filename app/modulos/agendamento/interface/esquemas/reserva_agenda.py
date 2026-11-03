from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.agendamento.dominio.entidades import SituacaoReserva


class ReservaAgendaResposta(BaseModel):
    id: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    situacao: SituacaoReserva
    id_solicitacao: int
    id_espaco: int
    ids_recursos: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DisponibilidadeReservaResposta(BaseModel):
    id_espaco: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    disponivel: bool
    motivo: str | None = None
