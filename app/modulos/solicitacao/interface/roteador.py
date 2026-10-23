from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.modulos.solicitacao.casos_uso.criar_solicitacao import (
    CriarSolicitacaoCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.anexar_arquivo import (
    AnexarArquivoSolicitacaoCasoDeUso,
    LIMITE_ANEXO_BYTES,
)
from app.modulos.solicitacao.casos_uso.listar_solicitacoes import (
    ListarSolicitacoesCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.obter_solicitacao import (
    ObterSolicitacaoCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.obter_url_anexo import (
    ObterUrlAnexoCasoDeUso,
)
from app.modulos.solicitacao.dominio.entidades import Solicitacao
from app.modulos.solicitacao.interface.dependencias import (
    pegar_caso_de_uso_criar_solicitacao,
    pegar_caso_de_uso_anexar_arquivo,
    pegar_caso_de_uso_listar_solicitacoes,
    pegar_caso_de_uso_obter_solicitacao,
    pegar_caso_de_uso_obter_url_anexo,
)
from app.modulos.solicitacao.interface.esquemas import (
    AnexoSolicitacaoResposta,
    CriarSolicitacao,
    SolicitacaoResposta,
    UrlAnexoResposta,
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


@roteador.post(
    "/{id_solicitacao}/anexos",
    response_model=AnexoSolicitacaoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Anexar um documento PDF ou DOCX à solicitação",
)
def anexar_arquivo(
    id_solicitacao: int,
    arquivo: UploadFile = File(...),
    usuario_logado: Usuario = Depends(apenas_servidor),
    caso_de_uso: AnexarArquivoSolicitacaoCasoDeUso = Depends(
        pegar_caso_de_uso_anexar_arquivo
    ),
) -> AnexoSolicitacaoResposta:
    conteudo = arquivo.file.read(LIMITE_ANEXO_BYTES + 1)
    return caso_de_uso.executar(
        id_solicitacao=id_solicitacao,
        id_solicitante=usuario_logado.id,
        nome_arquivo=arquivo.filename,
        conteudo=conteudo,
    )


@roteador.get(
    "/{id_solicitacao}/anexos/{id_anexo}/url",
    response_model=UrlAnexoResposta,
    status_code=status.HTTP_200_OK,
    summary="Gerar um link temporário para baixar um anexo",
)
def obter_url_anexo(
    id_solicitacao: int,
    id_anexo: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ObterUrlAnexoCasoDeUso,
        Depends(pegar_caso_de_uso_obter_url_anexo),
    ],
) -> UrlAnexoResposta:
    url, validade = caso_de_uso.executar(
        id_solicitacao,
        id_anexo,
        usuario_logado,
    )
    return UrlAnexoResposta(
        url_assinada=url,
        validade_segundos=validade,
    )


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