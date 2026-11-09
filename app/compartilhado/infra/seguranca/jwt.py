from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from app.compartilhado.infra.config import config
from app.modulos.usuarios.dominio.contratos import TokenContrato


class JWT(TokenContrato):
    def criar_token_acesso(self, id_usuario: int, id_sessao: str) -> str:
        agora = datetime.now(UTC)

        payload = {
            "sub": str(id_usuario),
            "sid": id_sessao,
            "typ": "access",
            "jti": str(uuid4()),
            "iat": agora,
            "exp": agora + timedelta(minutes=config.minutos_expiracao_token),
        }

        return jwt.encode(
            payload,
            config.chave_secreta,
            algorithm="HS256",
        )