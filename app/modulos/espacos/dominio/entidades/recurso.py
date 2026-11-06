from __future__ import annotations

from pydantic import Field

from app.compartilhado.dominio.entidade_base import EntidadeBase
from .reserva_associada import ReservaAssociada


class Recurso(EntidadeBase):
    nome: str
    tipo: str
    autorizacao_necessaria: bool = False
    disponibilidade: bool = True
    reserva_independente: bool = False
    id_espaco: int
    reservas: list[ReservaAssociada] = Field(default_factory=list)
