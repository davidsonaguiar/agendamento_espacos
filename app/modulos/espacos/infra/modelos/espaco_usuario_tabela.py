from sqlalchemy import Column, ForeignKey, Integer, Table

from app.compartilhado.infra.banco_dados import Base

espaco_usuario_tabela = Table(
    "espaco_usuario",
    Base.metadata,
    Column("id_espaco", Integer, ForeignKey("espaco.id", ondelete="CASCADE"), primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True)
)
