from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modulos.espacos.casos_uso.gerenciar_pausa_espaco import (
    GerenciarPausasEspacoCasoDeUso,
)
from app.modulos.espacos.interface.dependencias import (
    pegar_caso_de_uso_gerenciar_pausas,
)
from app.modulos.espacos.interface.esquemas import (
    CriarPausaFuncionamento,
    PausaResposta,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import (
    VerificarPerfil,
    obter_usuario_atual,
)

roteador = APIRouter()

admin_ou_coordenador = VerificarPerfil(
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR]
)


@roteador.post(
    "/{id_espaco}/pausas",
    response_model=PausaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar pausa de funcionamento (Admin/Coordenador)",
)
def adicionar_pausa_espaco(
    id_espaco: int,
    dados: CriarPausaFuncionamento,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarPausasEspacoCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_pausas)
    ],
):
    return caso_de_uso.adicionar(id_espaco, dados)


@roteador.get(
    "/{id_espaco}/pausas",
    response_model=list[PausaResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar pausas de funcionamento do espaço (Todos os perfis)",
)
def listar_pausas_espaco(
    id_espaco: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarPausasEspacoCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_pausas)
    ],
):
    return caso_de_uso.listar(id_espaco)


@roteador.delete(
    "/{id_espaco}/pausas/{id_pausa}",
    status_code=status.HTTP_200_OK,
    summary="Remover pausa de funcionamento (Admin/Coordenador)",
)
def remover_pausa_espaco(
    id_espaco: int,
    id_pausa: int,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarPausasEspacoCasoDeUso, Depends(pegar_caso_de_uso_gerenciar_pausas)
    ],
):
    return caso_de_uso.remover(id_espaco, id_pausa)
