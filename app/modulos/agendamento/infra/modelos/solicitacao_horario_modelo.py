from sqlalchemy import Column, Date, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class SolicitacaoHorarioModelo(Base):
    __tablename__ = "solicitacao_horario"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_reserva = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    id_solicitacao = Column(
        Integer,
        ForeignKey("solicitacao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    solicitacao = relationship("SolicitacaoModelo", back_populates="horarios")
