from __future__ import annotations

from pydantic import ConfigDict, Field

from app.compartilhado.dominio.entidade_base import EntidadeBase

from .espaco_horario_funcionamento import EspacoHorarioFuncionamento
from .espaco_pausa_funcionamento import EspacoPausaFuncionamento
from .espaco_usuario_vinculado import EspacoUsuarioVinculado
from .recurso import Recurso


class Espaco(EntidadeBase):
    nome: str
    descricao: str | None = None
    capacidade: int | None = None
    bloco: str | None = None
    disponibilidade: bool = True
    recursos: list[Recurso] = Field(default_factory=list)
    usuarios_vinculados: list[EspacoUsuarioVinculado] = Field(default_factory=list)
    horarios_funcionamento: list[EspacoHorarioFuncionamento] = Field(
        default_factory=list
    )
    pausas_funcionamento: list[EspacoPausaFuncionamento] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
