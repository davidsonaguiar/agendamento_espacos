from pydantic import BaseModel, EmailStr, Field, SecretStr


class CriarMembro(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF apenas números ou formatado")
    vinculo_institucional: str = Field(
        ..., min_length=3, description="Matrícula ou vínculo institucional"
    )
    email: EmailStr
    senha: SecretStr = Field(..., min_length=8)
