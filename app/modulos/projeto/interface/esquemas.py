from pydantic import BaseModel, ConfigDict, Field

from app.modulos.projeto.dominio.entidades import (
    AtualizacaoProjeto,
    NovoProjeto,
    Projeto,
    StatusProjeto,
)


class CriarProjeto(NovoProjeto):
    pass


class AtualizarProjeto(AtualizacaoProjeto):
    pass


class AvaliarProjeto(BaseModel):
    status: StatusProjeto


class AdicionarParticipante(BaseModel):
    id_usuario: int = Field(..., gt=0)
    papel_no_projeto: str = Field(..., min_length=2, max_length=100)


class ProjetoResposta(Projeto):
    model_config = ConfigDict(from_attributes=True)