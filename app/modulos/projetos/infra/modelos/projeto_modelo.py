from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class ProjetoModelo(Base):
    __tablename__ = "projeto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(255), nullable=False)
    finalidade = Column(String(255), nullable=False)
    id_responsavel = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_criador = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    quantidade_participantes = Column(Integer, nullable=True)
    documentacao_base = Column(String(500), nullable=True)

    participantes = relationship(
        "ProjetoParticipanteModelo",
        back_populates="projeto",
        cascade="all, delete-orphan",
    )
