from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, event, inspect, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.compartilhado.infra.banco_dados import Base
from app.modulos.usuarios.infra.modelos.usuario_modelo import UsuarioModelo


class SessaoAutenticacaoModelo(Base):
    __tablename__ = "sessao_autenticacao"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expira_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    revogada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    tokens: Mapped[list["RefreshTokenModelo"]] = relationship(
        back_populates="sessao",
        cascade="all, delete-orphan",
    )


class RefreshTokenModelo(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_sessao: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessao_autenticacao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hash_token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expira_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    consumido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sessao: Mapped[SessaoAutenticacaoModelo] = relationship(
        back_populates="tokens"
    )


class TokenRedefinicaoSenhaModelo(Base):
    __tablename__ = "token_redefinicao_senha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hash_token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    usado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


@event.listens_for(UsuarioModelo, "before_update")
def revogar_sessoes_apos_alteracao_de_credenciais(_mapper, connection, usuario):
    estado = inspect(usuario)
    senha_alterada = estado.attrs.senha_codificada.history.has_changes()
    usuario_desativado = (
        estado.attrs.ativo.history.has_changes() and not usuario.ativo
    )
    if senha_alterada or usuario_desativado:
        connection.execute(
            update(SessaoAutenticacaoModelo)
            .where(
                SessaoAutenticacaoModelo.id_usuario == usuario.id,
                SessaoAutenticacaoModelo.revogada_em.is_(None),
            )
            .values(revogada_em=datetime.now(UTC))
        )
