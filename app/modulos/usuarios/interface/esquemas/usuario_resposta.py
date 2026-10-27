from pydantic import BaseModel, ConfigDict, EmailStr

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


class UsuarioResposta(BaseModel):
    id: int
    nome_completo: str
    cpf: str
    vinculo_institucional: str
    email: EmailStr
    perfil: PerfilUsuario
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
