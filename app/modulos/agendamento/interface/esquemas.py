from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modulos.agendamento.dominio.entidades import (
    Solicitacao,
    TipoSolicitacao,
)


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


class NovaSolicitacao(BaseModel):
    tipo: TipoSolicitacao
    finalidade: str = Field(..., min_length=3, max_length=255)
    urgencia: bool = False
    id_projeto: int | None = Field(None, gt=0)
    id_espaco: int = Field(..., gt=0)
    ids_usuarios_envolvidos: list[int] = Field(default_factory=list)
    horarios: list[NovoHorarioSolicitacao] = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")

    @field_validator("ids_usuarios_envolvidos")
    @classmethod
    def validar_usuarios_envolvidos(cls, ids: list[int]) -> list[int]:
        if any(id_usuario <= 0 for id_usuario in ids):
            raise ValueError("Os IDs dos usuários envolvidos devem ser positivos.")
        if len(ids) != len(set(ids)):
            raise ValueError("Não informe usuários envolvidos duplicados.")
        return ids


class CriarSolicitacao(NovaSolicitacao):
    pass


class AnexoSolicitacaoResposta(BaseModel):
    id: int
    nome_arquivo: str
    tipo_arquivo: str
    data_upload: datetime

    model_config = ConfigDict(from_attributes=True)


class SolicitacaoResposta(Solicitacao):
    anexos: list[AnexoSolicitacaoResposta] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UrlAnexoResposta(BaseModel):
    url_assinada: str
    validade_segundos: int