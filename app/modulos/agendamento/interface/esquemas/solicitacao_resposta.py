from pydantic import ConfigDict, Field

from app.modulos.agendamento.dominio.entidades import Solicitacao

from .anexo_solicitacao_resposta import AnexoSolicitacaoResposta


class SolicitacaoResposta(Solicitacao):
    anexos: list[AnexoSolicitacaoResposta] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
