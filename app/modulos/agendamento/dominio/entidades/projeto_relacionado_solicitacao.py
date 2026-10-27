from __future__ import annotations

from app.compartilhado.dominio.entidade_base import EntidadeBase


class ProjetoRelacionadoSolicitacao(EntidadeBase):
    descricao: str
    finalidade: str
