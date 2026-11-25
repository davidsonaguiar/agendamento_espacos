from pydantic import BaseModel, ConfigDict
from pydantic import Field

from .reserva_associada_resposta import ReservaAssociadaResposta


class RecursoResposta(BaseModel):
    id: int
    nome: str
    tipo: str
    autorizacao_necessaria: bool
    disponibilidade: bool
    reserva_independente: bool
    id_espaco: int
    reservas: list[ReservaAssociadaResposta] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
