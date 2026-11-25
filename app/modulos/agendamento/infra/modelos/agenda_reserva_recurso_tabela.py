from sqlalchemy import Column, ForeignKey, Integer, Table

from app.compartilhado.infra.banco_dados import Base

agenda_reserva_recurso_tabela = Table(
    "agenda_reserva_recurso",
    Base.metadata,
    Column(
        "id_agenda",
        Integer,
        ForeignKey("agenda_reserva.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_recurso",
        Integer,
        ForeignKey("recurso.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
