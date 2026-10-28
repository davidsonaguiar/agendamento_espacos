from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class RecursoModelo(Base):
    __tablename__ = "recurso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(100), nullable=False)
    autorizacao_necessaria = Column(Boolean, default=False, nullable=False)
    disponibilidade = Column(Boolean, default=True, nullable=False)
    reserva_independente = Column(Boolean, default=False, nullable=False)
    id_espaco = Column(
        Integer, ForeignKey("espaco.id", ondelete="CASCADE"), nullable=False
    )
    espaco = relationship("EspacoModelo", back_populates="recursos")
