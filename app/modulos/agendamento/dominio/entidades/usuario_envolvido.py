from __future__ import annotations

from app.compartilhado.dominio.entidade_base import EntidadeBase


class UsuarioEnvolvido(EntidadeBase):
    id_usuario: int
    nome_completo: str
