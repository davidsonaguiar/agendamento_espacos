from datetime import time

from pydantic import BaseModel, ConfigDict


class HorarioFuncionamentoResposta(BaseModel):
    id: int
    dia_semana: int
    hora_abertura: time
    hora_fechamento: time
    ativo: bool
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)
