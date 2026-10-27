from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Time
from sqlalchemy.orm import relationship

from app.compartilhado.infra.banco_dados import Base

espaco_usuario_tabela = Table(
    "espaco_usuario",
    Base.metadata,
    Column("id_espaco", Integer, ForeignKey("espaco.id", ondelete="CASCADE"), primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True)
)

class EspacoModelo(Base):
    __tablename__ = "espaco"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(String(255), nullable=True)
    capacidade = Column(Integer, nullable=True)
    bloco = Column(String(50), nullable=True)
    disponibilidade = Column(Boolean, default=True, nullable=False)

    usuarios_vinculados = relationship(
        "UsuarioModelo",
        secondary=espaco_usuario_tabela,
        backref="espacos_vinculados",
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

class EspacoHorarioFuncionamentoModelo(Base):
    __tablename__ = "espaco_horario_funcionamento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dia_semana = Column(Integer, nullable=False)
    hora_abertura = Column(Time, nullable=False)
    hora_fechamento = Column(Time, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False) # Nova coluna!
    id_espaco = Column(Integer, ForeignKey("espaco.id", ondelete="CASCADE"), nullable=False)
    espaco = relationship("EspacoModelo", back_populates="horarios_funcionamento")

class EspacoPausaFuncionamentoModelo(Base):
    __tablename__ = "espaco_pausa_funcionamento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    motivo = Column(String(200), nullable=False)
    id_espaco = Column(Integer, ForeignKey("espaco.id", ondelete="CASCADE"), nullable=False)
    espaco = relationship("EspacoModelo", back_populates="pausas_funcionamento")