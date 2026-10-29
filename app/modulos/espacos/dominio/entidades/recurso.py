from __future__ import annotations

from app.compartilhado.dominio.entidade_base import EntidadeBase


class Recurso(EntidadeBase):
    nome: str
    tipo: str
    autorizacao_necessaria: bool = False
    disponibilidade: bool = True
    reserva_independente: bool = False
    id_espaco: int
