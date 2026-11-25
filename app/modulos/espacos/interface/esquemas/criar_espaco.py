from pydantic import BaseModel, Field


class CriarEspaco(BaseModel):
    nome: str = Field(..., min_length=3, description="Nome da sala ou laboratório (ex: COLAB Maker)")
    descricao: str | None = Field(None, description="Descrição dos equipamentos ou finalidade do espaço")
    capacidade: int | None = Field(None, description="Capacidade máxima de pessoas (ex: 20 pessoas)")
    bloco: str | None = Field(None, description="Localização física no campus (ex: Bloco de Informática)")
    disponibilidade: bool = Field(True, description="Indica se o espaço está ativo para uso")
