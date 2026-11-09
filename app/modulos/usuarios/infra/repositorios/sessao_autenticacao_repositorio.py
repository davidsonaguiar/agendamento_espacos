from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modulos.usuarios.infra.modelos import (
    RefreshTokenModelo,
    SessaoAutenticacaoModelo,
)


class SessaoAutenticacaoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def criar(
        self,
        id_usuario: int,
        hash_refresh_token: str,
        expira_em: datetime,
    ) -> str:
        agora = datetime.now(UTC)
        sessoes_expiradas = (
            self.db.query(SessaoAutenticacaoModelo)
            .filter(
                or_(
                    SessaoAutenticacaoModelo.expira_em <= agora,
                    SessaoAutenticacaoModelo.revogada_em.is_not(None),
                )
            )
            .all()
        )
        for sessao_expirada in sessoes_expiradas:
            self.db.delete(sessao_expirada)

        id_sessao = str(uuid4())
        sessao = SessaoAutenticacaoModelo(
            id=id_sessao,
            id_usuario=id_usuario,
            criada_em=agora,
            expira_em=expira_em,
        )
        sessao.tokens.append(
            RefreshTokenModelo(
                hash_token=hash_refresh_token,
                criado_em=agora,
                expira_em=expira_em,
            )
        )
        self.db.add(sessao)
        self.db.commit()
        return id_sessao

    def buscar_refresh_token(self, hash_token: str) -> RefreshTokenModelo | None:
        return (
            self.db.query(RefreshTokenModelo)
            .filter(RefreshTokenModelo.hash_token == hash_token)
            .with_for_update()
            .first()
        )

    def rotacionar(
        self,
        token_atual: RefreshTokenModelo,
        novo_hash: str,
        expira_em: datetime,
    ) -> None:
        agora = datetime.now(UTC)
        token_atual.consumido_em = agora
        token_atual.sessao.expira_em = expira_em
        token_atual.sessao.tokens.append(
            RefreshTokenModelo(
                hash_token=novo_hash,
                criado_em=agora,
                expira_em=expira_em,
            )
        )
        self.db.commit()

    def sessao_ativa(self, id_sessao: str, id_usuario: int) -> bool:
        sessao = (
            self.db.query(SessaoAutenticacaoModelo)
            .filter(
                SessaoAutenticacaoModelo.id == id_sessao,
                SessaoAutenticacaoModelo.id_usuario == id_usuario,
                SessaoAutenticacaoModelo.revogada_em.is_(None),
            )
            .first()
        )
        return bool(sessao and _data_utc(sessao.expira_em) > datetime.now(UTC))

    def revogar(self, id_sessao: str) -> None:
        self.db.query(SessaoAutenticacaoModelo).filter(
            SessaoAutenticacaoModelo.id == id_sessao,
            SessaoAutenticacaoModelo.revogada_em.is_(None),
        ).update(
            {SessaoAutenticacaoModelo.revogada_em: datetime.now(UTC)},
            synchronize_session=False,
        )
        self.db.commit()

    def revogar_todas(self, id_usuario: int) -> None:
        self.db.query(SessaoAutenticacaoModelo).filter(
            SessaoAutenticacaoModelo.id_usuario == id_usuario,
            SessaoAutenticacaoModelo.revogada_em.is_(None),
        ).update(
            {SessaoAutenticacaoModelo.revogada_em: datetime.now(UTC)},
            synchronize_session=False,
        )
        self.db.commit()


def _data_utc(data: datetime) -> datetime:
    return data.replace(tzinfo=UTC) if data.tzinfo is None else data.astimezone(UTC)
