from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import Enum as SQLEnum

from app.compartilhado.infra.banco_dados import Base
from app.modulos.usuarios.dominio.entidades import PerfilUsuario


class UsuarioModelo(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(150), nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    vinculo_institucional = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_codificada = Column(String(255), nullable=False)
    perfil = Column(SQLEnum(PerfilUsuario), nullable=False)
    ativo = Column(Boolean, default=True)
