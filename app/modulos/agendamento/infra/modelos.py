from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.compartilhado.infra.banco_dados import Base


class ReservaAgendaModelo(Base):
    __tablename__ = "agenda_reserva"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_hora_inicio = Column(DateTime(timezone=False), nullable=False, index=True)
    data_hora_fim = Column(DateTime(timezone=False), nullable=False)
    situacao = Column(String(50), nullable=False, default="Confirmada")
    id_solicitacao = Column(
        Integer,
        ForeignKey("solicitacao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_espaco = Column(
        Integer,
        ForeignKey("espaco.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
