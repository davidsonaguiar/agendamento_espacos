from __future__ import annotations

from enum import Enum


class TipoSolicitacao(str, Enum):
    ESPACO = "Espaço"
    RECURSO = "Recurso"
    SERVICO = "Serviço"
