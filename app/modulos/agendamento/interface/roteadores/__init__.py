from fastapi import APIRouter

from . import agendamentos, solicitacoes

roteador = APIRouter(tags=["Agendamento"])
for roteador_modulo in (agendamentos, solicitacoes):
    roteador.include_router(roteador_modulo.roteador)

__all__ = ["roteador"]
