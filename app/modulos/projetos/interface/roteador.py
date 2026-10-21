from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.modulos.projetos.casos_uso.atualizar_projeto import (
    AtualizarProjetoCasoDeUso,
)
from app.modulos.projetos.casos_uso.criar_projeto import CriarProjetoCasoDeUso
from app.modulos.projetos.casos_uso.excluir_projeto import ExcluirProjetoCasoDeUso
from app.modulos.projetos.casos_uso.gerenciar_participantes import (
    GerenciarParticipantesCasoDeUso,
)
from app.modulos.projetos.casos_uso.listar_projetos import ListarProjetosCasoDeUso
from app.modulos.projetos.casos_uso.obter_projeto import ObterProjetoCasoDeUso
from app.modulos.projetos.dominio.entidade import Projeto
from app.modulos.projetos.interface.dependencias import (
    pegar_caso_de_uso_atualizar_projeto,
    pegar_caso_de_uso_criar_projeto,
    pegar_caso_de_uso_excluir_projeto,
    pegar_caso_de_uso_gerenciar_participantes,
    pegar_caso_de_uso_listar_projetos,
    pegar_caso_de_uso_obter_projeto,
)
from app.modulos.projetos.interface.esquemas import (
    AdicionarParticipante,
    AtualizarProjeto,
    CriarProjeto,
    ProjetoResposta,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import (
    VerificarPerfil,
    obter_usuario_atual,
)

roteador = APIRouter(prefix="/projetos", tags=["Projetos"])

apenas_admin = VerificarPerfil([PerfilUsuario.ADMINISTRADOR])

criadores_de_projeto = VerificarPerfil(
    [
        PerfilUsuario.ADMINISTRADOR,
        PerfilUsuario.COORDENADOR,
        PerfilUsuario.SERVIDOR,
        PerfilUsuario.MONITOR,
    ]
)


@roteador.post(
    "/",
    response_model=ProjetoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um projeto (Administrador, Coordenador, Servidor ou Monitor)",
)
def criar_projeto(
    dados: CriarProjeto,
    usuario_logado: Annotated[Usuario, Depends(criadores_de_projeto)],
    caso_de_uso: Annotated[
        CriarProjetoCasoDeUso, Depends(pegar_caso_de_uso_criar_projeto)
    ],
) -> Projeto:
    return caso_de_uso.executar(dados, usuario_logado)


@roteador.get(
    "/",
    response_model=list[ProjetoResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar projetos (Usuários autenticados)",
)
def listar_projetos(
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ListarProjetosCasoDeUso, Depends(pegar_caso_de_uso_listar_projetos)
    ],
) -> list[Projeto]:
    return caso_de_uso.executar(usuario_logado)


@roteador.get(
    "/{id_projeto}",
    response_model=ProjetoResposta,
    status_code=status.HTTP_200_OK,
    summary="Consultar um projeto",
)
def obter_projeto(
    id_projeto: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ObterProjetoCasoDeUso, Depends(pegar_caso_de_uso_obter_projeto)
    ],
) -> Projeto:
    return caso_de_uso.executar(id_projeto, usuario_logado)


@roteador.put(
    "/{id_projeto}",
    response_model=ProjetoResposta,
    status_code=status.HTTP_200_OK,
    summary="Atualizar dados do próprio projeto",
)
def atualizar_projeto(
    id_projeto: int,
    dados: AtualizarProjeto,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        AtualizarProjetoCasoDeUso, Depends(pegar_caso_de_uso_atualizar_projeto)
    ],
) -> Projeto:
    return caso_de_uso.executar(
        id_projeto, usuario_logado.id, dados
    )


@roteador.delete(
    "/{id_projeto}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir um projeto (Criador ou Administrador)",
)
def excluir_projeto(
    id_projeto: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ExcluirProjetoCasoDeUso, Depends(pegar_caso_de_uso_excluir_projeto)
    ],
) -> Response:
    caso_de_uso.executar(id_projeto, usuario_logado)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@roteador.post(
    "/{id_projeto}/participantes",
    response_model=ProjetoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar participante (Responsável ou Administrador)",
)
def adicionar_participante(
    id_projeto: int,
    dados: AdicionarParticipante,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarParticipantesCasoDeUso,
        Depends(pegar_caso_de_uso_gerenciar_participantes),
    ],
) -> Projeto:
    return caso_de_uso.adicionar(
        id_projeto,
        dados.id_usuario,
        usuario_logado.id,
        dados.papel_no_projeto,
        usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR,
    )


@roteador.delete(
    "/{id_projeto}/participantes/{id_usuario}",
    response_model=ProjetoResposta,
    status_code=status.HTTP_200_OK,
    summary="Remover participante (Responsável ou Administrador)",
)
def remover_participante(
    id_projeto: int,
    id_usuario: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarParticipantesCasoDeUso,
        Depends(pegar_caso_de_uso_gerenciar_participantes),
    ],
) -> Projeto:
    return caso_de_uso.remover(
        id_projeto,
        id_usuario,
        usuario_logado.id,
        usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR,
    )
