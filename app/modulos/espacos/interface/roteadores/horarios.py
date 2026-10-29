from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modulos.espacos.casos_uso.atualizar_horarios_espaco import (
    AtualizarHorariosEspacoCasoDeUso,
)
from app.modulos.espacos.interface.dependencias import (
    pegar_caso_de_uso_atualizar_horarios_espaco,
)
from app.modulos.espacos.interface.esquemas import AtualizarHorario
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import VerificarPerfil

roteador = APIRouter()

admin_ou_coordenador = VerificarPerfil(
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR]
)


@roteador.patch(
    "/{id_espaco}/horarios",
    status_code=status.HTTP_200_OK,
    summary="Atualizar horário de funcionamento do espaço (Admin/Coordenador)",
)
def atualizar_horario_funcionamento(
    id_espaco: int,
    dados: AtualizarHorario,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        AtualizarHorariosEspacoCasoDeUso,
        Depends(pegar_caso_de_uso_atualizar_horarios_espaco),
    ],
):
    return caso_de_uso.executar(id_espaco, dados)
