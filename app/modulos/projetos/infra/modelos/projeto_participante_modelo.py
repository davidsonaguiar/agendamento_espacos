from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base
from app.modulos.usuarios.infra.modelos import UsuarioModelo


class ProjetoParticipanteModelo(Base):
    __tablename__ = "projeto_participante"

    id_projeto = Column(Integer, ForeignKey("projeto.id", ondelete="CASCADE"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True)
    papel_no_projeto = Column(String(100), nullable=False)
    projeto = relationship("ProjetoModelo", back_populates="participantes")
    usuario = relationship(UsuarioModelo)
