from pydantic import BaseModel, Field


class CriarRecurso(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., min_length=1, max_length=100)
    autorizacao_necessaria: bool = False
    reserva_independente: bool = False
