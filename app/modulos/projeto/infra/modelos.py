from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base
from app.modulos.projeto.dominio.entidades import StatusProjeto
from app.modulos.usuarios.infra.modelos import UsuarioModelo


class ProjetoModelo(Base):
    __tablename__ = "projeto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(255), nullable=False)
    finalidade = Column(String(255), nullable=False)
    id_responsavel = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    quantidade_participantes = Column(Integer, nullable=True)
    documentacao_base = Column(String(500), nullable=True)
    status = Column(
        SQLEnum(
            StatusProjeto,
            name="status_projeto",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=StatusProjeto.PENDENTE,
        nullable=False,
    )

    participantes = relationship(
        "ProjetoParticipanteModelo",
        back_populates="projeto",
        cascade="all, delete-orphan",
    )


class ProjetoParticipanteModelo(Base):
    __tablename__ = "projeto_participante"

    id_projeto = Column(
        Integer, ForeignKey("projeto.id", ondelete="CASCADE"), primary_key=True
    )
    id_usuario = Column(
        Integer, ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )
    papel_no_projeto = Column(String(100), nullable=False)

    projeto = relationship("ProjetoModelo", back_populates="participantes")
    usuario = relationship(UsuarioModelo)