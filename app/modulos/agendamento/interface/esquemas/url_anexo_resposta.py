from pydantic import BaseModel


class UrlAnexoResposta(BaseModel):
    url_assinada: str
    validade_segundos: int
