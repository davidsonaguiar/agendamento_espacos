from __future__ import annotations

from enum import Enum


class StatusSolicitacao(str, Enum):
    PENDENTE = "Pendente"
    CANCELADA = "Cancelada"
