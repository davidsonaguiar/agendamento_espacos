from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class SolicitacaoInteracaoModelo(Base):
    __tablename__ = "solicitacao_interacao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), nullable=False, index=True)
    situacao = Column(String(50), nullable=False)
    mensagem = Column(Text, nullable=False)
    dados = Column(JSON, nullable=True)
    data_criacao = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    id_solicitacao = Column(
        Integer,
        ForeignKey("solicitacao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )

    solicitacao = relationship("SolicitacaoModelo", back_populates="interacoes")
