from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class AnexoSolicitacaoModelo(Base):
    __tablename__ = "anexo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_arquivo = Column(String(255), nullable=False)
    url_caminho = Column(String(500), nullable=False)
    tipo_arquivo = Column(String(100), nullable=False)
    data_upload = Column(DateTime(timezone=True), nullable=False)
    id_solicitacao = Column(
        Integer,
        ForeignKey("solicitacao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    solicitacao = relationship("SolicitacaoModelo", back_populates="anexos")
