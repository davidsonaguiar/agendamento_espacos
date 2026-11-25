from __future__ import annotations

from datetime import date

from pydantic import ConfigDict, model_validator

from app.compartilhado.dominio.entidade_base import EntidadeBase
from app.compartilhado.dominio.erros import RegraDeNegocioErro


class EspacoPausaFuncionamento(EntidadeBase):
    data_inicio: date
    data_fim: date
    motivo: str
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def validar_datas(self):
        if self.data_fim < self.data_inicio:
            raise RegraDeNegocioErro("A data final do bloqueio não pode ser anterior à data inicial.")
        return self
