from __future__ import annotations

from app.compartilhado.dominio.entidade_base import EntidadeBase


class SolicitanteSolicitacao(EntidadeBase):
    nome_completo: str
    perfil: str
