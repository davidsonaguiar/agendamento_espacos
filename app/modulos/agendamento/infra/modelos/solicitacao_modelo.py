from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base
from app.modulos.agendamento.dominio.entidades import TipoSolicitacao
from app.modulos.espacos.infra.modelos import EspacoModelo
from app.modulos.projetos.infra.modelos import ProjetoModelo
from app.modulos.usuarios.infra.modelos import UsuarioModelo

from .solicitacao_usuario_tabela import solicitacao_usuario_tabela


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
