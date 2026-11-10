from pydantic import BaseModel, Field, SecretStr


class AlterarSenha(BaseModel):
    senha_atual: SecretStr
    nova_senha: SecretStr = Field(..., min_length=8)
