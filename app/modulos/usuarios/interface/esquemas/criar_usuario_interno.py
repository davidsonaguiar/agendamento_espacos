from pydantic import BaseModel, EmailStr, Field, SecretStr
from app.modulos.usuarios.dominio.entidades import PerfilUsuario


class CriarUsuarioInterno(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14)
    vinculo_institucional: str = Field(..., min_length=3)
    email: EmailStr
    senha: SecretStr = Field(..., min_length=8)
    perfil: PerfilUsuario = Field(..., description="O perfil do usuário que será criado")
