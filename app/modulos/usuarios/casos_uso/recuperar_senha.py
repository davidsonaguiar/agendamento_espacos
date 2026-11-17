from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from html import escape
import secrets
from urllib.parse import urlencode

from app.compartilhado.dominio.erros import ColabErro
from app.modulos.usuarios.dominio.contratos import (
    CodificadorSenhaContrato,
    UsuarioRepositorioContrato,
)
from app.modulos.usuarios.infra.repositorios import (
    TokenRedefinicaoSenhaRepositorio,
)


class SolicitarRecuperacaoSenhaCasoDeUso:
    def __init__(
        self,
        usuarios: UsuarioRepositorioContrato,
        tokens: TokenRedefinicaoSenhaRepositorio,
        enviar_email: Callable[[str, str, str], None],
        url_frontend: str,
        minutos_validade_token: int,
    ):
        self.usuarios = usuarios
        self.tokens = tokens
        self.enviar_email = enviar_email
        self.url_frontend = url_frontend.rstrip("/")
        self.minutos_validade_token = minutos_validade_token

    def executar(self, email: str) -> None:
        usuario = self.usuarios.buscar_por_email(email)
        if usuario is None or not usuario.ativo:
            return

        token = secrets.token_urlsafe(32)
        hash_token = sha256(token.encode("utf-8")).hexdigest()
        self.tokens.criar(
            id_usuario=usuario.id,
            hash_token=hash_token,
            expira_em=datetime.now(UTC)
            + timedelta(minutes=self.minutos_validade_token),
        )
        link = (
            f"{self.url_frontend}/recuperar-senha?"
            f"{urlencode({'token': token})}"
        )
        nome = escape(usuario.nome_completo)
        link_html = escape(link, quote=True)
        self.enviar_email(
            usuario.email,
            "Redefinição de senha",
            (
                f"<p>Olá, {nome}.</p>"
                "<p>Recebemos uma solicitação para redefinir sua senha. "
                "Use o link abaixo:</p>"
                f'<p><a href="{link_html}">Redefinir minha senha</a></p>'
                f"<p>Este link expira em {self.minutos_validade_token} minutos. "
                "Se você não solicitou a redefinição, ignore este e-mail.</p>"
            ),
        )


class RedefinirSenhaCasoDeUso:
    def __init__(
        self,
        tokens: TokenRedefinicaoSenhaRepositorio,
        codificador: CodificadorSenhaContrato,
    ):
        self.tokens = tokens
        self.codificador = codificador

    def executar(self, token: str, nova_senha: str) -> None:
        hash_token = sha256(token.encode("utf-8")).hexdigest()
        senha_codificada = self.codificador.codificar_senha(nova_senha)
        if not self.tokens.redefinir_senha(hash_token, senha_codificada):
            raise ColabErro(
                status_code=400,
                detail="Link de redefinição inválido ou expirado.",
            )
