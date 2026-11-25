from datetime import time

from pydantic import BaseModel, Field


class AtualizarHorario(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6, description="0=Domingo, 1=Segunda, ..., 6=Sábado")
    hora_abertura: time = Field(..., description="Horário de abertura, ex: 08:00")
    hora_fechamento: time = Field(..., description="Horário de fechamento, ex: 18:00")
    ativo: bool = Field(..., description="Define se o laboratório funciona neste dia específico")
