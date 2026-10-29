from __future__ import annotations

from datetime import date, time

from app.compartilhado.dominio.entidade_base import EntidadeBase


class HorarioSolicitacao(EntidadeBase):
    data_reserva: date
    hora_inicio: time
    hora_fim: time
