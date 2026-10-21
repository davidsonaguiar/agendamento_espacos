from pydantic import ConfigDict

from app.modulos.solicitacao.dominio.entidades import (
    NovaSolicitacao,
    Solicitacao,
)


class CriarSolicitacao(NovaSolicitacao):
    pass


class SolicitacaoResposta(Solicitacao):
    model_config = ConfigDict(from_attributes=True)