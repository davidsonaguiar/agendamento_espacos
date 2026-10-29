from __future__ import annotations

from datetime import datetime

from pydantic import ConfigDict, Field

from app.compartilhado.dominio.entidade_base import EntidadeBase

from .anexo_solicitacao import AnexoSolicitacao
from .espaco_relacionado_solicitacao import EspacoRelacionadoSolicitacao
from .horario_solicitacao import HorarioSolicitacao
from .projeto_relacionado_solicitacao import ProjetoRelacionadoSolicitacao
from .solicitante_solicitacao import SolicitanteSolicitacao
from .status_solicitacao import (
    SituacaoInteracaoSolicitacao,
    StatusSolicitacao,
    TipoInteracaoSolicitacao,
)
from .tipo_solicitacao import TipoSolicitacao
from .usuario_envolvido import UsuarioEnvolvido


class InteracaoSolicitacao(EntidadeBase):
    id: int
    tipo: TipoInteracaoSolicitacao
    situacao: SituacaoInteracaoSolicitacao
    mensagem: str
    dados: dict[str, object] | None = None
    id_usuario: int
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)


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
    ids_recursos: list[int] = Field(default_factory=list)
    horarios: list[HorarioSolicitacao] = Field(default_factory=list)
    anexos: list[AnexoSolicitacao] = Field(default_factory=list)
    interacoes: list[InteracaoSolicitacao] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
