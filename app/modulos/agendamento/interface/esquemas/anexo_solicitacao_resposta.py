from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnexoSolicitacaoResposta(BaseModel):
    id: int
    nome_arquivo: str
    tipo_arquivo: str
    data_upload: datetime

    model_config = ConfigDict(from_attributes=True)
