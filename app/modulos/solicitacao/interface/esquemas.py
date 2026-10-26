from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.solicitacao.dominio.entidades import (
    DecisaoSolicitacao,
    NovaSolicitacao,
    Solicitacao,
)


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


class DecidirSolicitacao(DecisaoSolicitacao):
    pass