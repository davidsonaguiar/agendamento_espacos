from __future__ import annotations

from datetime import datetime

from app.compartilhado.dominio.entidade_base import EntidadeBase


class AnexoSolicitacao(EntidadeBase):
    id: int
    nome_arquivo: str
    url_caminho: str
    tipo_arquivo: str
    data_upload: datetime
