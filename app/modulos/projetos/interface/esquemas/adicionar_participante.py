from pydantic import BaseModel, Field


class AdicionarParticipante(BaseModel):
    id_usuario: int = Field(..., gt=0)
    papel_no_projeto: str = Field(..., min_length=2, max_length=100)
