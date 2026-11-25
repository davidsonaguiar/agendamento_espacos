from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base
from .espaco_usuario_tabela import espaco_usuario_tabela


class EspacoUsuarioModelo(Base):
    __table__ = espaco_usuario_tabela

    espaco = relationship("EspacoModelo", back_populates="vinculos_usuarios")
    usuario = relationship("UsuarioModelo", back_populates="vinculos_espacos")
