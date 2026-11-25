from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modulos.espacos.casos_uso.gerenciar_vinculos import GerenciarVinculosCasoDeUso
from app.modulos.espacos.interface.dependencias import (
    pegar_caso_de_uso_gerenciar_vinculos,
)
from app.modulos.espacos.interface.esquemas import (
    UsuarioVinculadoResposta,
    VincularUsuario,
)
from app.modulos.usuarios.dominio.entidades import Usuario
from app.modulos.usuarios.interface.seguranca_http import obter_usuario_atual

roteador = APIRouter()


@roteador.delete(
    "/{id_espaco}/usuarios/{id_usuario}",
    status_code=status.HTTP_200_OK,
    summary="Remover vínculo de usuário com o Espaço (Admin/Coordenador)",
)
def desvincular_usuario_espaco(
    id_espaco: int,
    id_usuario: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarVinculosCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_vinculos)
    ],
):
    return caso_de_uso.desvincular(id_espaco, id_usuario, usuario_logado)


@roteador.post(
    "/{id_espaco}/usuarios/{id_usuario}",
    status_code=status.HTTP_201_CREATED,
    summary="Vincular coordenador ou monitor a um espaço",
)
def vincular_usuario_espaco(
    id_espaco: int,
    id_usuario: int,
    dados: VincularUsuario,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarVinculosCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_vinculos)
    ],
):
    return caso_de_uso.vincular(
        id_espaco, id_usuario, dados.perfil_espaco, usuario_logado
    )


@roteador.get(
    "/{id_espaco}/usuarios/disponiveis",
    response_model=list[UsuarioVinculadoResposta],
    summary="Listar membros disponíveis para vínculo no espaço",
)
def listar_usuarios_disponiveis(
    id_espaco: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarVinculosCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_vinculos)
    ],
):
    return caso_de_uso.listar_disponiveis(id_espaco, usuario_logado)
