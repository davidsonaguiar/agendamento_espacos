from pydantic import BaseModel, Field


class CriarProjeto(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=255)
    finalidade: str = Field(..., min_length=3, max_length=255)
    id_responsavel: int = Field(..., gt=0)
    quantidade_participantes: int | None = Field(None, ge=0)
    documentacao_base: str | None = Field(None, max_length=500)
