from __future__ import annotations

from app.compartilhado.dominio.entidade_base import EntidadeBase

from .perfil_espaco import PerfilEspaco


class EspacoUsuarioVinculado(EntidadeBase):
    id_usuario: int
    nome_completo: str
    perfil_espaco: PerfilEspaco | None = None
