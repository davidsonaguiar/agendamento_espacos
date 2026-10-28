from pydantic import BaseModel, ConfigDict


class UsuarioVinculadoResposta(BaseModel):
    id_usuario: int
    nome_completo: str

    model_config = ConfigDict(from_attributes=True)
