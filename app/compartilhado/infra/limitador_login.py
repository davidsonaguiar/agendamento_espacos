from hashlib import sha256
from math import ceil
from time import time

from fastapi import HTTPException, Request, status
from limits import parse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.compartilhado.infra.config import config

_LIMITE_LOGIN = parse("5/5 minutes")

limitador_login = Limiter(
    key_func=get_remote_address,
    storage_uri=config.rate_limit_storage_uri,
)


def verificar_bloqueio_login(request: Request, identificacao: str) -> str:
    chave = _criar_chave(request, identificacao)
    if limitador_login.limiter.test(_LIMITE_LOGIN, chave):
        return chave

    janela = limitador_login.limiter.get_window_stats(_LIMITE_LOGIN, chave)
    retry_after = max(1, ceil(janela.reset_time - time()))
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Muitas tentativas de login. Tente novamente em alguns minutos.",
        headers={"Retry-After": str(retry_after)},
    )


def registrar_falha_login(chave: str) -> None:
    limitador_login.limiter.hit(_LIMITE_LOGIN, chave)


def limpar_falhas_login(chave: str) -> None:
    limitador_login.limiter.clear(_LIMITE_LOGIN, chave)


def _criar_chave(request: Request, identificacao: str) -> str:
    identificacao_normalizada = identificacao.strip().lower()
    ip = get_remote_address(request)
    return sha256(f"{identificacao_normalizada}:{ip}".encode("utf-8")).hexdigest()
