from datetime import date

from pydantic import BaseModel, Field


class CriarPausaFuncionamento(BaseModel):
    data_inicio: date
    data_fim: date
    motivo: str = Field(..., min_length=3, description="Ex: Manutenção da serra, Feriado nacional")
