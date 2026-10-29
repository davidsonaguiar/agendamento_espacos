from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class EspacoPausaFuncionamentoModelo(Base):
    __tablename__ = "espaco_pausa_funcionamento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    motivo = Column(String(200), nullable=False)
    id_espaco = Column(Integer, ForeignKey("espaco.id", ondelete="CASCADE"), nullable=False)
    espaco = relationship("EspacoModelo", back_populates="pausas_funcionamento")
