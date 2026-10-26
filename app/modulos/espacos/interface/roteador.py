from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.modulos.espacos.casos_uso.atualizar_espaco import AtualizarEspacoCasoDeUso
from app.modulos.espacos.casos_uso.atualizar_horarios_espaco import (
    AtualizarHorariosEspacoCasoDeUso,
)
from app.modulos.espacos.casos_uso.cadastrar_espaco import CadastrarEspacoCasoDeUso
from app.modulos.espacos.casos_uso.desativar_espaco import DesativarEspacoCasoDeUso
from app.modulos.espacos.casos_uso.gerenciar_pausa_espaco import (
    GerenciarPausasEspacoCasoDeUso,
)
from app.modulos.espacos.casos_uso.gerenciar_vinculos import GerenciarVinculosCasoDeUso
from app.modulos.espacos.casos_uso.listar_espacos import ListarEspacosCasoDeUso
from app.modulos.espacos.casos_uso.listar_horarios_espaco import (
    ListarHorariosEspacoCasoDeUso,
)
from app.modulos.espacos.casos_uso.reativar_espaco import ReativarEspacoCasoDeUso
from app.modulos.espacos.interface.dependencias import (
    pegar_caso_de_uso_atualizar_espaco,
    pegar_caso_de_uso_atualizar_horarios_espaco,
    pegar_caso_de_uso_cadastrar_espaco,
    pegar_caso_de_uso_desativar_espaco,
    pegar_caso_de_uso_gerenciar_pausas,
    pegar_caso_de_uso_gerenciar_vinculos,
    pegar_caso_de_uso_listar_espacos,
    pegar_caso_de_uso_listar_horarios_espaco,
    pegar_caso_de_uso_reativar_espaco,
)
from app.modulos.espacos.interface.esquemas import (
    AtualizarEspaco,
    AtualizarHorario,
    CriarEspaco,
    CriarPausaFuncionamento,
    EspacoResposta,
    HorarioFuncionamentoResposta,
    PausaResposta,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import (
    VerificarPerfil,
    obter_usuario_atual,
)

roteador = APIRouter(prefix="/espacos", tags=["Infraestrutura e Espaços"])

apenas_admin = VerificarPerfil([PerfilUsuario.ADMINISTRADOR])
admin_ou_coordenador = VerificarPerfil(
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR]
)


@roteador.post(
    "/",
    response_model=EspacoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo espaço físico/sala (Somente Admin)",
)
def cadastrar_espaco(
    dados: CriarEspaco,
    usuario_logado: Annotated[Usuario, Depends(apenas_admin)],
    caso_de_uso: Annotated[
        CadastrarEspacoCasoDeUso, Depends(pegar_caso_de_uso_cadastrar_espaco)
    ],
):
    return caso_de_uso.executar(dados)


@roteador.get(
    "/",
    response_model=list[EspacoResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar espaços do laboratório com paginação e filtro por perfil (Disponível para todos os perfis)",
)
def listar_espacos(
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ListarEspacosCasoDeUso, Depends(pegar_caso_de_uso_listar_espacos)
    ],
    skip: Annotated[
        int, Query(ge=0, description="Número de registros para pular (Offset)")
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1, le=100, description="Limite máximo de registros retornados (Max 100)"
        ),
    ] = 100,
):
    return caso_de_uso.executar(usuario_logado, skip=skip, limit=limit)


@roteador.delete(
    "/{id_espaco}",
    response_model=EspacoResposta,
    status_code=status.HTTP_200_OK,
    summary="Desativar/Indisponibilizar um espaço (Somente Admin)",
)
def desativar_espaco(
    id_espaco: int,
    usuario_logado: Annotated[Usuario, Depends(apenas_admin)],
    caso_de_uso: Annotated[
        DesativarEspacoCasoDeUso, Depends(pegar_caso_de_uso_desativar_espaco)
    ],
):
    return caso_de_uso.executar(id_espaco)


@roteador.put(
    "/{id_espaco}",
    response_model=EspacoResposta,
    status_code=status.HTTP_200_OK,
    summary="Atualizar dados de um espaço (Admin e Coordenador)",
)
def atualizar_espaco(
    id_espaco: int,
    dados: AtualizarEspaco,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[
        AtualizarEspacoCasoDeUso, Depends(pegar_caso_de_uso_atualizar_espaco)
    ],
):
    return caso_de_uso.executar(id_espaco, dados)


@roteador.patch(
    "/{id_espaco}/reativar",
    response_model=EspacoResposta,
    status_code=status.HTTP_200_OK,
    summary="Reativar um espaço indisponível (Somente Admin)",
)
def reativar_espaco(
    id_espaco: int,
    usuario_logado: Annotated[Usuario, Depends(apenas_admin)],
    caso_de_uso: Annotated[
        ReativarEspacoCasoDeUso, Depends(pegar_caso_de_uso_reativar_espaco)
    ],
):
    return caso_de_uso.executar(id_espaco)


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


@roteador.get(
    "/{id_espaco}/horarios",
    response_model=list[HorarioFuncionamentoResposta],
    status_code=status.HTTP_200_OK,
    summary="Consultar horários de funcionamento do espaço",
)
def listar_horarios_funcionamento(
    id_espaco: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ListarHorariosEspacoCasoDeUso,
        Depends(pegar_caso_de_uso_listar_horarios_espaco),
    ],
):
    return caso_de_uso.executar(id_espaco)


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


@roteador.delete(
    "/{id_espaco}/usuarios/{id_usuario}",
    status_code=status.HTTP_200_OK,
    summary="Remover vínculo de Coordenador/Monitor com o Espaço (Somente Admin e Coordenador)",
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
