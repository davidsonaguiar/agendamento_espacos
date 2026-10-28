from __future__ import annotations
from app.compartilhado.dominio.entidade_base import EntidadeBase


class EspacoRelacionadoSolicitacao(EntidadeBase):
    nome: str
    descricao: str | None = None
    capacidade: int | None = None
    bloco: str | None = None
    disponibilidade: bool
