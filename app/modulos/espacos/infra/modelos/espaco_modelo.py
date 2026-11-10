from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base


class EspacoModelo(Base):
    __tablename__ = "espaco"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(String(255), nullable=True)
    capacidade = Column(Integer, nullable=True)
    bloco = Column(String(50), nullable=True)
    disponibilidade = Column(Boolean, default=True, nullable=False)

    vinculos_usuarios = relationship(
        "EspacoUsuarioModelo",
        back_populates="espaco",
        cascade="all, delete-orphan",
    )
    horarios_funcionamento = relationship(
        "EspacoHorarioFuncionamentoModelo",
        back_populates="espaco",
        cascade="all, delete-orphan",
        order_by="EspacoHorarioFuncionamentoModelo.dia_semana",
    )
    pausas_funcionamento = relationship(
        "EspacoPausaFuncionamentoModelo",
        back_populates="espaco",
        cascade="all, delete-orphan",
        order_by="EspacoPausaFuncionamentoModelo.data_inicio",
    )
    recursos = relationship(
        "RecursoModelo",
        back_populates="espaco",
        cascade="all, delete-orphan",
        order_by="RecursoModelo.id",
    )
