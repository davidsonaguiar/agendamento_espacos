from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class NovoHorarioSolicitacao(BaseModel):
    data_reserva: date
    hora_inicio: time
    hora_fim: time

    model_config = ConfigDict(extra="forbid")

    @field_validator("hora_inicio", "hora_fim")
    @classmethod
    def validar_fuso_horario(cls, valor: time) -> time:
        if valor.tzinfo is not None and valor.utcoffset() is not None:
            raise ValueError("Informe os horários no fuso local, sem deslocamento.")
        return valor

    @model_validator(mode="after")
    def validar_intervalo(self) -> NovoHorarioSolicitacao:
        agora = datetime.now()
        if self.hora_fim <= self.hora_inicio:
            raise ValueError("A hora final deve ser posterior à hora inicial.")
        if self.data_reserva < agora.date():
            raise ValueError("A data do horário deve ser futura.")
        if self.data_reserva == agora.date() and self.hora_inicio <= agora.time():
            raise ValueError("O horário de início deve ser futuro.")
        return self
