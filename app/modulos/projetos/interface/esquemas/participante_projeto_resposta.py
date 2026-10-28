from pydantic import BaseModel, ConfigDict


class ParticipanteProjetoResposta(BaseModel):
    id_usuario: int
    nome_completo: str
    papel_no_projeto: str

    model_config = ConfigDict(from_attributes=True)
