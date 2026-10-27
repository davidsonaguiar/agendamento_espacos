from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.modulos.espacos.casos_uso.gerenciar_recursos_espaco import (
    GerenciarRecursosEspacoCasoDeUso,
)
from app.modulos.espacos.interface.dependencias import (
    pegar_caso_de_uso_gerenciar_recursos,
)
from app.modulos.espacos.interface.esquemas import (
    AtualizarRecurso,
    CriarRecurso,
    RecursoResposta,
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
    "/{id_espaco}/recursos",
    response_model=RecursoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar recurso em um espaço (Admin/Coordenador)",
)
def adicionar_recurso_espaco(
    id_espaco: int,
    dados: CriarRecurso,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarRecursosEspacoCasoDeUso,
        Depends(pegar_caso_de_uso_gerenciar_recursos),
    ],
):
    return caso_de_uso.adicionar(id_espaco, dados)


@roteador.put(
    "/{id_espaco}/recursos/{id_recurso}",
    response_model=RecursoResposta,
    status_code=status.HTTP_200_OK,
    summary="Atualizar recurso de um espaço (Admin/Coordenador)",
)
def atualizar_recurso_espaco(
    id_espaco: int,
    id_recurso: int,
    dados: AtualizarRecurso,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarRecursosEspacoCasoDeUso,
        Depends(pegar_caso_de_uso_gerenciar_recursos),
    ],
):
    return caso_de_uso.atualizar(id_espaco, id_recurso, dados)


@roteador.delete(
    "/{id_espaco}/recursos/{id_recurso}",
    response_model=RecursoResposta,
    status_code=status.HTTP_200_OK,
    summary="Indisponibilizar recurso de um espaço (Admin/Coordenador)",
)
def indisponibilizar_recurso_espaco(
    id_espaco: int,
    id_recurso: int,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        GerenciarRecursosEspacoCasoDeUso,
        Depends(pegar_caso_de_uso_gerenciar_recursos),
    ],
):
    return caso_de_uso.indisponibilizar(id_espaco, id_recurso)


@roteador.get(
    "/{id_espaco}/recursos",
    response_model=list[RecursoResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar recursos de um espaço (Usuários autenticados)",
)
def listar_recursos_espaco(
    id_espaco: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarRecursosEspacoCasoDeUso,
        Depends(pegar_caso_de_uso_gerenciar_recursos),
    ],
    skip: Annotated[
        int, Query(ge=0, description="Número de recursos a ignorar")
    ] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Máximo de recursos retornados")
    ] = 100,
):
    return caso_de_uso.listar(
        id_espaco,
        usuario_logado,
        skip=skip,
        limit=limit,
    )
