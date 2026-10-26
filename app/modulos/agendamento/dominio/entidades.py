from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum

from pydantic import ConfigDict, Field

from app.compartilhado.dominio.entidade_base import EntidadeBase


class TipoSolicitacao(str, Enum):
    ESPACO = "Espaço"
    RECURSO = "Recurso"
    SERVICO = "Serviço"


class StatusSolicitacao(str, Enum):
    PENDENTE = "Pendente"
    CANCELADA = "Cancelada"


class UsuarioEnvolvido(EntidadeBase):
    id_usuario: int
    nome_completo: str


class HorarioSolicitacao(EntidadeBase):
    data_reserva: date
    hora_inicio: time
    hora_fim: time


class AnexoSolicitacao(EntidadeBase):
    id: int
    nome_arquivo: str
    url_caminho: str
    tipo_arquivo: str
    data_upload: datetime


class ProjetoRelacionadoSolicitacao(EntidadeBase):
    descricao: str
    finalidade: str


class EspacoRelacionadoSolicitacao(EntidadeBase):
    nome: str
    descricao: str | None = None
    capacidade: int | None = None
    bloco: str | None = None
    disponibilidade: bool


class SolicitanteSolicitacao(EntidadeBase):
    nome_completo: str
    perfil: str


class Solicitacao(EntidadeBase):
    id: int | None = None
    tipo: TipoSolicitacao
    finalidade: str
    urgencia: bool
    status: str = StatusSolicitacao.PENDENTE.value
    decisao_justificativa: str | None = None
    id_projeto: int | None = None
    id_solicitante: int
    id_espaco: int
    projeto: ProjetoRelacionadoSolicitacao | None = None
    espaco: EspacoRelacionadoSolicitacao | None = None
    solicitante: SolicitanteSolicitacao | None = None
    usuarios_envolvidos: list[UsuarioEnvolvido] = Field(default_factory=list)
    horarios: list[HorarioSolicitacao] = Field(default_factory=list)
    anexos: list[AnexoSolicitacao] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)