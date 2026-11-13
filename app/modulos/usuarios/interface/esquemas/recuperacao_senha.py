from pydantic import BaseModel, EmailStr, Field, SecretStr


class SolicitarRecuperacaoSenha(BaseModel):
    email: EmailStr


class RedefinirSenha(BaseModel):
    token: SecretStr = Field(min_length=43, max_length=128)
    nova_senha: SecretStr = Field(min_length=8)
