from pydantic import BaseModel

from .usuario_resposta import UsuarioResposta


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResposta
