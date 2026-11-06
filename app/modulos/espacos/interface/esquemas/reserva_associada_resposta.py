from datetime import datetime

from pydantic import BaseModel


class ReservaAssociadaResposta(BaseModel):
    id: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    situacao: str
    id_solicitacao: int
    id_espaco: int
    espaco_reservado: bool
    ids_recursos: list[int]
