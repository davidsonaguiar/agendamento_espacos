from fastapi import APIRouter

from . import espacos, horarios, pausas, recursos, vinculos

roteador = APIRouter(prefix="/espacos", tags=["Infraestrutura e Espaço"])
for roteador_modulo in (espacos, horarios, pausas, recursos, vinculos):
    roteador.include_router(roteador_modulo.roteador)

__all__ = ["roteador"]
