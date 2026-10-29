from sqlalchemy import Column, ForeignKey, Integer, Table

from app.compartilhado.infra.banco_dados import Base

solicitacao_recurso_tabela = Table(
    "solicitacao_recurso",
    Base.metadata,
    Column(
        "id_solicitacao",
        Integer,
        ForeignKey("solicitacao.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_recurso",
        Integer,
        ForeignKey("recurso.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
