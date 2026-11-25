from pydantic import BaseModel, Field, SecretStr


class UsuarioLogin(BaseModel):
    identificacao: str = Field(..., description="Pode ser o CPF (apenas números ou formatado) ou E-mail")
    senha: SecretStr = Field(..., description="Senha em texto puro para validação")
