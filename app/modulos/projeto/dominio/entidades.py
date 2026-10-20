from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StatusProjeto(str, Enum):
    PENDENTE = "Pendente"
    ACEITO = "Aceito"
    RECUSADO = "Recusado"


class NovoProjeto(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=255)
    finalidade: str = Field(..., min_length=3, max_length=255)
    quantidade_participantes: int | None = Field(None, ge=0)
    documentacao_base: str | None = Field(None, max_length=500)


class AtualizacaoProjeto(BaseModel):
    descricao: str | None = Field(None, min_length=3, max_length=255)
    finalidade: str | None = Field(None, min_length=3, max_length=255)
    quantidade_participantes: int | None = Field(None, ge=0)
    documentacao_base: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def validar_campos_obrigatorios(self) -> AtualizacaoProjeto:
        for campo in ("descricao", "finalidade"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"{campo} não pode ser nulo.")
        return self


class ParticipanteProjeto(BaseModel):
    id_usuario: int
    nome_completo: str
    papel_no_projeto: str


class Projeto(BaseModel):
    id: int | None = None
    descricao: str
    finalidade: str
    id_responsavel: int
    quantidade_participantes: int | None = None
    documentacao_base: str | None = None
    status: StatusProjeto = StatusProjeto.PENDENTE
    participantes: list[ParticipanteProjeto] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)