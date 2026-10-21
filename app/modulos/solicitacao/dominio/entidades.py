from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoSolicitacao(str, Enum):
    ESPACO = "Espaço"
    RECURSO = "Recurso"
    SERVICO = "Serviço"


class StatusSolicitacao(str, Enum):
    PENDENTE = "Pendente"


class NovaSolicitacao(BaseModel):
    tipo: TipoSolicitacao
    finalidade: str = Field(..., min_length=3, max_length=255)
    urgencia: bool = False
    id_projeto: int | None = Field(None, gt=0)
    id_espaco: int = Field(..., gt=0)
    ids_usuarios_envolvidos: list[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("ids_usuarios_envolvidos")
    @classmethod
    def validar_usuarios_envolvidos(cls, ids: list[int]) -> list[int]:
        if any(id_usuario <= 0 for id_usuario in ids):
            raise ValueError("Os IDs dos usuários envolvidos devem ser positivos.")
        if len(ids) != len(set(ids)):
            raise ValueError("Não informe usuários envolvidos duplicados.")
        return ids


class UsuarioEnvolvido(BaseModel):
    id_usuario: int
    nome_completo: str


class Solicitacao(BaseModel):
    id: int | None = None
    tipo: TipoSolicitacao
    finalidade: str
    urgencia: bool
    status: str = StatusSolicitacao.PENDENTE.value
    decisao_justificativa: str | None = None
    id_projeto: int | None = None
    id_solicitante: int
    id_espaco: int
    usuarios_envolvidos: list[UsuarioEnvolvido] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)