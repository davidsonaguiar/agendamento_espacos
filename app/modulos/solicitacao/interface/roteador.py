from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.modulos.solicitacao.casos_uso.criar_solicitacao import (
    CriarSolicitacaoCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.listar_solicitacoes import (
    ListarSolicitacoesCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.obter_solicitacao import (
    ObterSolicitacaoCasoDeUso,
)
from app.modulos.solicitacao.dominio.entidades import Solicitacao
from app.modulos.solicitacao.interface.dependencias import (
    pegar_caso_de_uso_criar_solicitacao,
    pegar_caso_de_uso_listar_solicitacoes,
    pegar_caso_de_uso_obter_solicitacao,
)
from app.modulos.solicitacao.interface.esquemas import (
    CriarSolicitacao,
    SolicitacaoResposta,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import (
    VerificarPerfil,
    obter_usuario_atual,
)

roteador = APIRouter(prefix="/solicitacoes", tags=["Solicitações"])
apenas_servidor = VerificarPerfil([PerfilUsuario.SERVIDOR])


def _id_usuario_autenticado(usuario: Usuario) -> int:
    if usuario.id is None:
        raise CredenciaisInvalidasErro()
    return usuario.id


@roteador.post(
    "/",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar uma solicitação (Servidor)",
)
def criar_solicitacao(
    dados: CriarSolicitacao,
    usuario_logado: Annotated[Usuario, Depends(apenas_servidor)],
    caso_de_uso: Annotated[
        CriarSolicitacaoCasoDeUso,
        Depends(pegar_caso_de_uso_criar_solicitacao),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(
        dados, _id_usuario_autenticado(usuario_logado)
    )


@roteador.get(
    "/",
    response_model=list[SolicitacaoResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar solicitações próprias ou todas para gestores",
)
def listar_solicitacoes(
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ListarSolicitacoesCasoDeUso,
        Depends(pegar_caso_de_uso_listar_solicitacoes),
    ],
) -> list[Solicitacao]:
    return caso_de_uso.executar(usuario_logado)


@roteador.get(
    "/{id_solicitacao}",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Consultar uma solicitação própria ou de gestor",
)
def obter_solicitacao(
    id_solicitacao: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ObterSolicitacaoCasoDeUso,
        Depends(pegar_caso_de_uso_obter_solicitacao),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(id_solicitacao, usuario_logado)