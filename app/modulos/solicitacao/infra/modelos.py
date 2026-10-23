from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Table,
    Time,
)
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base
from app.modulos.espacos.infra.modelos import EspacoModelo
from app.modulos.projetos.infra.modelos import ProjetoModelo
from app.modulos.solicitacao.dominio.entidades import TipoSolicitacao
from app.modulos.usuarios.infra.modelos import UsuarioModelo

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


class SolicitacaoModelo(Base):
    __tablename__ = "solicitacao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(
        SQLEnum(
            TipoSolicitacao,
            name="tipo_solicitacao",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    finalidade = Column(String(255), nullable=False)
    urgencia = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="Pendente", nullable=False)
    decisao_justificativa = Column(String(1000), nullable=True)
    id_projeto = Column(Integer, ForeignKey("projeto.id"), nullable=True)
    id_solicitante = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_espaco = Column(Integer, ForeignKey("espaco.id"), nullable=False)

    projeto = relationship(ProjetoModelo)
    solicitante = relationship(UsuarioModelo, foreign_keys=[id_solicitante])
    espaco = relationship(EspacoModelo)
    usuarios_envolvidos = relationship(
        UsuarioModelo,
        secondary=solicitacao_usuario_tabela,
    )
    horarios = relationship(
        "SolicitacaoHorarioModelo",
        back_populates="solicitacao",
        cascade="all, delete-orphan",
        order_by="SolicitacaoHorarioModelo.data_reserva, SolicitacaoHorarioModelo.hora_inicio",
    )
    anexos = relationship(
        "AnexoSolicitacaoModelo",
        back_populates="solicitacao",
        cascade="all, delete-orphan",
        order_by="AnexoSolicitacaoModelo.data_upload",
    )


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