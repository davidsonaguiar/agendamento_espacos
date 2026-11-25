from __future__ import annotations

from datetime import time

from pydantic import ConfigDict, Field, model_validator

from app.compartilhado.dominio.entidade_base import EntidadeBase
from app.compartilhado.dominio.erros import RegraDeNegocioErro


class EspacoHorarioFuncionamento(EntidadeBase):
    dia_semana: int = Field(
        ..., ge=0, le=6, description="0=Domingo, 1=Segunda, ..., 6=Sábado"
    )
    hora_abertura: time
    hora_fechamento: time
    ativo: bool = True
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validar_regras_horario(self):
        if self.hora_fechamento <= self.hora_abertura:
            raise RegraDeNegocioErro(
                f"Horário inválido para o dia {self.dia_semana}: "
                f"O fechamento ({self.hora_fechamento}) deve ser posterior à abertura ({self.hora_abertura})."
            )
        return self
