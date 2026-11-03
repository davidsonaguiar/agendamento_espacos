from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class StatusSolicitacao(str, Enum):
    PENDENTE = "Pendente"
    AGUARDANDO_COMPLEMENTACAO = "AguardandoComplementacao"
    AGUARDANDO_RESPOSTA_PROPOSTA = "AguardandoRespostaProposta"
    APROVADO = "Aprovado"
    REJEITADO = "Rejeitado"
    CANCELADA = "Cancelada"


class StatusDecisaoSolicitacao(str, Enum):
    APROVADO = StatusSolicitacao.APROVADO.value
    REJEITADO = StatusSolicitacao.REJEITADO.value


class DecisaoSolicitacao(BaseModel):
    status: StatusDecisaoSolicitacao
    justificativa: str = Field(..., min_length=3, max_length=1000)

    @field_validator("justificativa")
    @classmethod
    def validar_justificativa(cls, valor: str) -> str:
        justificativa = valor.strip()
        if len(justificativa) < 3:
            raise ValueError("A justificativa deve conter ao menos 3 caracteres.")
        return justificativa


class TipoInteracaoSolicitacao(str, Enum):
    COMPLEMENTACAO_SOLICITADA = "ComplementacaoSolicitada"
    COMPLEMENTACAO_RESPONDIDA = "ComplementacaoRespondida"
    REPLANEJAMENTO_PROPOSTO = "ReplanejamentoProposto"
    PROPOSTA_RESPONDIDA = "PropostaRespondida"


class SituacaoInteracaoSolicitacao(str, Enum):
    AGUARDANDO_RESPOSTA = "AguardandoResposta"
    RESPONDIDA = "Respondida"
    ACEITA = "Aceita"
    RECUSADA = "Recusada"
