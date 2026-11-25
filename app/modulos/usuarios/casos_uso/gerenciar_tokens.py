import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.compartilhado.infra.config import config
from app.modulos.usuarios.dominio.contratos import (
    TokenContrato,
    UsuarioRepositorioContrato,
)
from app.modulos.usuarios.dominio.entidades import Usuario
from app.modulos.usuarios.infra.repositorios import (
    SessaoAutenticacaoRepositorio,
)
from app.modulos.usuarios.interface.esquemas import TokenResposta


class GerenciarTokensCasoDeUso:
    def __init__(
        self,
        sessoes: SessaoAutenticacaoRepositorio,
        usuarios: UsuarioRepositorioContrato,
        token_servico: TokenContrato,
    ):
        self.sessoes = sessoes
        self.usuarios = usuarios
        self.token_servico = token_servico

    def emitir(self, usuario: Usuario) -> tuple[TokenResposta, str]:
        if usuario.id is None:
            raise RuntimeError("Não é possível emitir tokens para um usuário sem ID.")
        refresh_token = secrets.token_urlsafe(48)
        expira_em = datetime.now(UTC) + timedelta(
            days=config.dias_expiracao_refresh_token
        )
        id_sessao = self.sessoes.criar(
            id_usuario=usuario.id,
            hash_refresh_token=_hash_token(refresh_token),
            expira_em=expira_em,
        )
        return (
            self._resposta(usuario, id_sessao),
            refresh_token,
        )

    def renovar(self, refresh_token: str) -> tuple[TokenResposta, str]:
        token = self.sessoes.buscar_refresh_token(_hash_token(refresh_token))
        if token is None:
            raise CredenciaisInvalidasErro()

        sessao = token.sessao
        agora = datetime.now(UTC)
        if sessao.revogada_em is not None:
            raise CredenciaisInvalidasErro()

        if token.consumido_em is not None:
            self.sessoes.revogar(sessao.id)
            raise CredenciaisInvalidasErro()

        if (
            _data_utc(token.expira_em) <= agora
            or _data_utc(sessao.expira_em) <= agora
        ):
            self.sessoes.revogar(sessao.id)
            raise CredenciaisInvalidasErro()

        usuario = self.usuarios.buscar_por_id(sessao.id_usuario)
        if usuario is None or not usuario.ativo:
            self.sessoes.revogar(sessao.id)
            raise CredenciaisInvalidasErro()

        novo_refresh_token = secrets.token_urlsafe(48)
        nova_expiracao = agora + timedelta(
            days=config.dias_expiracao_refresh_token
        )
        self.sessoes.rotacionar(
            token_atual=token,
            novo_hash=_hash_token(novo_refresh_token),
            expira_em=nova_expiracao,
        )
        return (
            self._resposta(usuario, sessao.id),
            novo_refresh_token,
        )

    def revogar_refresh_token(self, refresh_token: str | None) -> None:
        if refresh_token is None:
            return
        token = self.sessoes.buscar_refresh_token(_hash_token(refresh_token))
        if token is not None:
            self.sessoes.revogar(token.id_sessao)

    def revogar_todas(self, id_usuario: int) -> None:
        self.sessoes.revogar_todas(id_usuario)

    def _resposta(self, usuario: Usuario, id_sessao: str) -> TokenResposta:
        if usuario.id is None:
            raise RuntimeError("Não é possível emitir tokens para um usuário sem ID.")
        return TokenResposta(
            access_token=self.token_servico.criar_token_acesso(
                id_usuario=usuario.id,
                id_sessao=id_sessao,
            ),
            usuario=usuario,
        )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _data_utc(data: datetime) -> datetime:
    return data.replace(tzinfo=UTC) if data.tzinfo is None else data.astimezone(UTC)
