from datetime import datetime

from app.compartilhado.dominio.entidade_base import EntidadeBase


class ReservaAssociada(EntidadeBase):
    id: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    situacao: str
    id_solicitacao: int
    id_espaco: int
    espaco_reservado: bool
    ids_recursos: list[int]
