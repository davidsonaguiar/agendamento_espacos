from pydantic import BaseModel, Field


class AtualizarEspaco(BaseModel):
    nome: str | None = Field(None, min_length=3, description="Novo nome da sala")
    descricao: str | None = Field(None, description="Nova descrição")
    capacidade: int | None = Field(None, description="Nova capacidade")
    bloco: str | None = Field(None, description="Novo bloco")
