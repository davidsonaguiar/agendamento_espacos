from pydantic import BaseModel, ConfigDict


class RecursoResposta(BaseModel):
    id: int
    nome: str
    tipo: str
    autorizacao_necessaria: bool
    disponibilidade: bool
    reserva_independente: bool
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)
