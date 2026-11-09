from fastapi import APIRouter

from . import agendamentos, solicitacoes

roteador = APIRouter(tags=["Agendamento"])
roteador.include_router(agendamentos.roteador)
roteador.include_router(solicitacoes.roteador)
