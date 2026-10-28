from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modulos.espacos.casos_uso.gerenciar_vinculos import GerenciarVinculosCasoDeUso
from app.modulos.espacos.interface.dependencias import (
    pegar_caso_de_uso_gerenciar_vinculos,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import VerificarPerfil

roteador = APIRouter()

admin_ou_coordenador = VerificarPerfil(
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR]
)


@roteador.delete(
    "/{id_espaco}/usuarios/{id_usuario}",
    status_code=status.HTTP_200_OK,
    summary="Remover vínculo de usuário com o Espaço (Admin/Coordenador)",
)
def desvincular_usuario_espaco(
    id_espaco: int,
    id_usuario: int,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarVinculosCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_vinculos)
    ],
):
    return caso_de_uso.desvincular(id_espaco, id_usuario)


@roteador.post(
    "/{id_espaco}/usuarios/{id_usuario}",
    status_code=status.HTTP_201_CREATED,
    summary="Vincular Coordenador/Monitor ao Espaço (Somente Admin e Coordenador)",
)
def vincular_usuario_espaco(
    id_espaco: int,
    id_usuario: int,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarVinculosCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_vinculos)
    ],
):
    return caso_de_uso.vincular(id_espaco, id_usuario)
