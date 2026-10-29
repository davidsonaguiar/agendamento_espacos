from sqlalchemy import Boolean, Column, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class EspacoHorarioFuncionamentoModelo(Base):
    __tablename__ = "espaco_horario_funcionamento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dia_semana = Column(Integer, nullable=False)
    hora_abertura = Column(Time, nullable=False)
    hora_fechamento = Column(Time, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False) # Nova coluna!
    id_espaco = Column(Integer, ForeignKey("espaco.id", ondelete="CASCADE"), nullable=False)
    espaco = relationship("EspacoModelo", back_populates="horarios_funcionamento")
