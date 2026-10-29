from sqlalchemy import Column, ForeignKey, Integer, Table

from app.compartilhado.infra.banco_dados import Base

solicitacao_usuario_tabela = Table(
    "solicitacao_usuario",
    Base.metadata,
    Column(
        "id_solicitacao",
        Integer,
        ForeignKey("solicitacao.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_usuario",
        Integer,
        ForeignKey("usuario.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
