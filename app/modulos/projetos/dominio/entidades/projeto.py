from pydantic import ConfigDict, Field

from app.compartilhado.dominio.entidade_base import EntidadeBase

from .participante_projeto import ParticipanteProjeto


class Projeto(EntidadeBase):
    id: int | None = None
    descricao: str
    finalidade: str
    id_responsavel: int
    id_criador: int
    quantidade_participantes: int | None = None
    documentacao_base: str | None = None
    participantes: list[ParticipanteProjeto] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
