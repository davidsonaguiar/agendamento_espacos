from urllib.parse import quote, urlparse

import httpx
from fastapi import status

from app.compartilhado.dominio.erros import ColabErro
from app.compartilhado.infra.config import config


class ArmazenamentoSupabase:
    def __init__(self) -> None:
        if not config.supabase_url or not config.supabase_service_role_key:
            raise ColabErro(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "O armazenamento de anexos não está configurado.",
            )

        self.url = config.supabase_url.rstrip("/")
        self.bucket = config.supabase_bucket_anexos
        self.chave = config.supabase_service_role_key.get_secret_value()

    def enviar(self, caminho: str, conteudo: bytes, tipo_conteudo: str) -> None:
        self._request(
            "POST",
            self._url_objeto(caminho),
            content=conteudo,
            headers={"Content-Type": tipo_conteudo, "x-upsert": "false"},
        )

    def remover(self, caminho: str) -> None:
        self._request("DELETE", self._url_objeto(caminho))

    def criar_url_assinada(self, caminho: str, validade_segundos: int) -> str:
        resposta = self._request(
            "POST",
            f"{self.url}/storage/v1/object/sign/"
            f"{quote(self.bucket, safe='')}/{quote(caminho, safe='/')}",
            json={"expiresIn": validade_segundos},
        )
        try:
            url_assinada = resposta.json()["signedURL"]
        except (ValueError, KeyError, TypeError) as erro:
            raise ColabErro(
                status.HTTP_502_BAD_GATEWAY,
                "O armazenamento retornou uma resposta inválida ao gerar o link.",
            ) from erro

        if not isinstance(url_assinada, str) or not url_assinada:
            raise ColabErro(
                status.HTTP_502_BAD_GATEWAY,
                "O armazenamento retornou uma resposta inválida ao gerar o link.",
            )
        if url_assinada.startswith("/storage/v1/"):
            return f"{self.url}{url_assinada}"
        if url_assinada.startswith("/"):
            return f"{self.url}/storage/v1{url_assinada}"

        url = urlparse(url_assinada)
        url_base = urlparse(self.url)
        if url.scheme == url_base.scheme and url.netloc == url_base.netloc:
            return url_assinada
        raise ColabErro(
            status.HTTP_502_BAD_GATEWAY,
            "O armazenamento retornou um link de download inválido.",
        )

    def _url_objeto(self, caminho: str) -> str:
        return (
            f"{self.url}/storage/v1/object/"
            f"{quote(self.bucket, safe='')}/{quote(caminho, safe='/')}"
        )

    def _request(
        self,
        metodo: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
        json: dict[str, int] | None = None,
    ) -> httpx.Response:
        cabecalhos = {
            "apikey": self.chave,
            "Authorization": f"Bearer {self.chave}",
        }
        if headers:
            cabecalhos.update(headers)
        try:
            resposta = httpx.request(
                metodo,
                url,
                headers=cabecalhos,
                timeout=30.0,
                content=content,
                json=json,
            )
            resposta.raise_for_status()
            return resposta
        except httpx.HTTPStatusError as erro:
            raise ColabErro(
                status.HTTP_502_BAD_GATEWAY,
                "O armazenamento de anexos rejeitou a operação.",
            ) from erro
        except httpx.RequestError as erro:
            raise ColabErro(
                status.HTTP_502_BAD_GATEWAY,
                "Não foi possível comunicar com o armazenamento de anexos.",
            ) from erro
