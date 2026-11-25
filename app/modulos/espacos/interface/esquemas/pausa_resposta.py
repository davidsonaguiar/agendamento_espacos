from datetime import date

from pydantic import BaseModel, ConfigDict


class PausaResposta(BaseModel):
    id: int
    data_inicio: date
    data_fim: date
    motivo: str
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)
