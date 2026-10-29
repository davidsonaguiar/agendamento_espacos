from pydantic import BaseModel, ConfigDict, Field

from .participante_projeto_resposta import ParticipanteProjetoResposta


class ProjetoResposta(BaseModel):
    id: int
    descricao: str
    finalidade: str
    id_responsavel: int
    id_criador: int
    quantidade_participantes: int | None = None
    documentacao_base: str | None = None
    participantes: list[ParticipanteProjetoResposta] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
