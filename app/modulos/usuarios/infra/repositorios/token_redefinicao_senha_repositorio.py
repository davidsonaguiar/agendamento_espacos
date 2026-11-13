from datetime import UTC, datetime

from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from app.modulos.usuarios.infra.modelos import (
    TokenRedefinicaoSenhaModelo,
    UsuarioModelo,
)


class TokenRedefinicaoSenhaRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def criar(
        self, id_usuario: int, hash_token: str, expira_em: datetime
    ) -> None:
        agora = datetime.now(UTC)
        self.db.execute(
            delete(TokenRedefinicaoSenhaModelo).where(
                TokenRedefinicaoSenhaModelo.id_usuario == id_usuario
            )
        )
        self.db.execute(
            delete(TokenRedefinicaoSenhaModelo).where(
                TokenRedefinicaoSenhaModelo.expira_em <= agora
            )
        )
        self.db.add(
            TokenRedefinicaoSenhaModelo(
                id_usuario=id_usuario,
                hash_token=hash_token,
                criado_em=agora,
                expira_em=expira_em,
            )
        )
        self.db.commit()

    def redefinir_senha(self, hash_token: str, senha_codificada: str) -> bool:
        agora = datetime.now(UTC)
        token = (
            self.db.query(TokenRedefinicaoSenhaModelo)
            .filter(
                TokenRedefinicaoSenhaModelo.hash_token == hash_token,
                TokenRedefinicaoSenhaModelo.usado_em.is_(None),
            )
            .with_for_update()
            .first()
        )
        if token is None or _data_utc(token.expira_em) <= agora:
            return False

        usuario = (
            self.db.query(UsuarioModelo)
            .filter(
                UsuarioModelo.id == token.id_usuario,
                UsuarioModelo.ativo.is_(True),
            )
            .with_for_update()
            .first()
        )
        if usuario is None:
            return False

        token.usado_em = agora
        usuario.senha_codificada = senha_codificada
        self.db.execute(
            update(TokenRedefinicaoSenhaModelo)
            .where(
                TokenRedefinicaoSenhaModelo.id_usuario == usuario.id,
                TokenRedefinicaoSenhaModelo.usado_em.is_(None),
            )
            .values(usado_em=agora)
        )
        self.db.commit()
        return True


def _data_utc(data: datetime) -> datetime:
    return data.replace(tzinfo=UTC) if data.tzinfo is None else data.astimezone(UTC)
