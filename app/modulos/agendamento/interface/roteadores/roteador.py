from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.modulos.agendamento.casos_uso.anexar_arquivo import (
    LIMITE_ANEXO_BYTES,
    AnexarArquivoSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.cancelar_solicitacao import (
    CancelarSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.criar_solicitacao import (
    CriarSolicitacaoCasoDeUso,
    DadosNovaSolicitacao,
)
from app.modulos.agendamento.casos_uso.listar_solicitacoes import (
    ListarSolicitacoesCasoDeUso,
)
from app.modulos.agendamento.casos_uso.decidir_solicitacao import (
    DecidirSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.obter_solicitacao import (
    ObterSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.obter_url_anexo import (
    ObterUrlAnexoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.propor_replanejamento import (
    ProporReplanejamentoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.responder_complementacao import (
    ResponderComplementacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.responder_proposta import (
    ResponderPropostaCasoDeUso,
)
from app.modulos.agendamento.casos_uso.solicitar_complementacao import (
    SolicitarComplementacaoCasoDeUso,
)
from app.modulos.agendamento.dominio.entidades import HorarioSolicitacao, Solicitacao
from app.modulos.agendamento.interface.dependencias import (
    pegar_caso_de_uso_anexar_arquivo,
    pegar_caso_de_uso_cancelar_solicitacao,
    pegar_caso_de_uso_criar_solicitacao,
    pegar_caso_de_uso_decidir_solicitacao,
    pegar_caso_de_uso_listar_solicitacoes,
    pegar_caso_de_uso_obter_solicitacao,
    pegar_caso_de_uso_obter_url_anexo,
    pegar_caso_de_uso_propor_replanejamento,
    pegar_caso_de_uso_responder_complementacao,
    pegar_caso_de_uso_responder_proposta,
    pegar_caso_de_uso_solicitar_complementacao,
)
from app.modulos.agendamento.interface.esquemas import (
    AnexoSolicitacaoResposta,
    CriarSolicitacao,
    DecidirSolicitacao,
    MensagemSolicitacao,
    ProporReplanejamento,
    ResponderProposta,
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
gestores_solicitacao = VerificarPerfil(
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR]
)


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
    dados_caso_de_uso = DadosNovaSolicitacao(
        tipo=dados.tipo,
        finalidade=dados.finalidade,
        urgencia=dados.urgencia,
        id_projeto=dados.id_projeto,
        id_espaco=dados.id_espaco,
        ids_recursos=dados.ids_recursos,
        ids_usuarios_envolvidos=dados.ids_usuarios_envolvidos,
        horarios=[
            HorarioSolicitacao(
                data_reserva=horario.data_reserva,
                hora_inicio=horario.hora_inicio,
                hora_fim=horario.hora_fim,
            )
            for horario in dados.horarios
        ],
    )
    return caso_de_uso.executar(
        dados_caso_de_uso, _id_usuario_autenticado(usuario_logado)
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


@roteador.patch(
    "/{id_solicitacao}/decisao",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Aprovar ou rejeitar uma solicitação",
)
def decidir_solicitacao(
    id_solicitacao: int,
    decisao: DecidirSolicitacao,
    usuario_logado: Annotated[Usuario, Depends(gestores_solicitacao)],
    caso_de_uso: Annotated[
        DecidirSolicitacaoCasoDeUso,
        Depends(pegar_caso_de_uso_decidir_solicitacao),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(id_solicitacao, decisao)


@roteador.post(
    "/{id_solicitacao}/complementacao",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Solicitar complementação de uma solicitação",
)
def solicitar_complementacao(
    id_solicitacao: int,
    dados: MensagemSolicitacao,
    usuario_logado: Annotated[Usuario, Depends(gestores_solicitacao)],
    caso_de_uso: Annotated[
        SolicitarComplementacaoCasoDeUso,
        Depends(pegar_caso_de_uso_solicitar_complementacao),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(
        id_solicitacao,
        _id_usuario_autenticado(usuario_logado),
        dados.mensagem,
    )


@roteador.post(
    "/{id_solicitacao}/complementacao/resposta",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Responder à solicitação de complementação",
)
def responder_complementacao(
    id_solicitacao: int,
    dados: MensagemSolicitacao,
    usuario_logado: Annotated[Usuario, Depends(apenas_servidor)],
    caso_de_uso: Annotated[
        ResponderComplementacaoCasoDeUso,
        Depends(pegar_caso_de_uso_responder_complementacao),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(
        id_solicitacao,
        _id_usuario_autenticado(usuario_logado),
        dados.mensagem,
    )


@roteador.post(
    "/{id_solicitacao}/propostas-replanejamento",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Propor novos horários e recursos para uma solicitação",
)
def propor_replanejamento(
    id_solicitacao: int,
    dados: ProporReplanejamento,
    usuario_logado: Annotated[Usuario, Depends(gestores_solicitacao)],
    caso_de_uso: Annotated[
        ProporReplanejamentoCasoDeUso,
        Depends(pegar_caso_de_uso_propor_replanejamento),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(
        id_solicitacao=id_solicitacao,
        id_usuario=_id_usuario_autenticado(usuario_logado),
        mensagem=dados.mensagem,
        horarios=[
            HorarioSolicitacao(
                data_reserva=horario.data_reserva,
                hora_inicio=horario.hora_inicio,
                hora_fim=horario.hora_fim,
            )
            for horario in dados.horarios
        ],
        ids_recursos=dados.ids_recursos,
    )


@roteador.post(
    "/{id_solicitacao}/propostas-replanejamento/{id_interacao}/resposta",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Aceitar ou recusar uma proposta de replanejamento",
)
def responder_proposta(
    id_solicitacao: int,
    id_interacao: int,
    dados: ResponderProposta,
    usuario_logado: Annotated[Usuario, Depends(apenas_servidor)],
    caso_de_uso: Annotated[
        ResponderPropostaCasoDeUso,
        Depends(pegar_caso_de_uso_responder_proposta),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(
        id_solicitacao,
        id_interacao,
        _id_usuario_autenticado(usuario_logado),
        dados.aceita,
        dados.mensagem,
    )


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


@roteador.patch(
    "/{id_solicitacao}",
    response_model=SolicitacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Cancelar uma solicitação própria ou por Administrador",
)
def cancelar_solicitacao(
    id_solicitacao: int,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        CancelarSolicitacaoCasoDeUso,
        Depends(pegar_caso_de_uso_cancelar_solicitacao),
    ],
) -> Solicitacao:
    return caso_de_uso.executar(id_solicitacao, usuario_logado)