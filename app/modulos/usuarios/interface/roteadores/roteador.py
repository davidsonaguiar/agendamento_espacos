from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Query, Response, status

from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.compartilhado.infra.config import config
from app.modulos.usuarios.casos_uso.alterar_senha import AlterarSenhaCasoDeUso
from app.modulos.usuarios.casos_uso.autenticar_usuario import AutenticarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.cadastrar_usuario import CadastrarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.gerenciar_tokens import GerenciarTokensCasoDeUso
from app.modulos.usuarios.casos_uso.listar_usuarios import ListarUsuariosCasoDeUso
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.dependencias import (
    pegar_caso_de_uso_alterar_senha,
    pegar_caso_de_uso_autenticacao,
    pegar_caso_de_uso_cadastro,
    pegar_caso_de_uso_listar_usuarios,
    pegar_caso_de_uso_tokens,
)
from app.modulos.usuarios.interface.esquemas import (
    AlterarSenha,
    CriarMembro,
    CriarUsuarioInterno,
    TokenResposta,
    UsuarioLogin,
    UsuarioResposta,
)
from app.modulos.usuarios.interface.seguranca_http import (
    VerificarPerfil,
    obter_usuario_atual,
)

roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])
apenas_admin = VerificarPerfil([PerfilUsuario.ADMINISTRADOR])

@roteador.post(
    "/servidor",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta de membro (Público)",
    deprecated=True,
    include_in_schema=False,
)
@roteador.post(
    "/",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta de membro (Público)",
)
def cadastrar_membro(
    dados: CriarMembro,
    caso_de_uso: Annotated[CadastrarUsuarioCasoDeUso, Depends(pegar_caso_de_uso_cadastro)]
):
    return caso_de_uso.membro(dados)


@roteador.post(
    "/interno",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um usuário (Somente Admin)"
)
def cadastrar_usuario_interno(
    dados: CriarUsuarioInterno,
    usuario_logado: Annotated[Usuario, Depends(apenas_admin)],
    caso_de_uso: Annotated[CadastrarUsuarioCasoDeUso, Depends(pegar_caso_de_uso_cadastro)]
):
    return caso_de_uso.interno(dados, usuario_logado)


@roteador.post(
    "/login",
    response_model=TokenResposta,
    status_code=status.HTTP_200_OK,
    summary="Autenticar Usuário - Login (Público)",
    description=(
        "Valida as credenciais do usuário, devolve o token JWT de acesso no "
        "corpo da resposta e define o refresh token no cabeçalho Set-Cookie. "
        "O cookie HttpOnly é armazenado e enviado automaticamente pelo navegador; "
        "não é exibido no JSON. (Público)"
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Login efetuado; access token no JSON e refresh token no cookie.",
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Define o cookie HttpOnly `refresh_token` (SameSite=Lax "
                        "e Secure por padrão)."
                    ),
                    "schema": {"type": "string"},
                }
            },
        }
    },
)
def login(
    resposta: Response,
    dados: UsuarioLogin,
    caso_de_uso: Annotated[AutenticarUsuarioCasoDeUso, Depends(pegar_caso_de_uso_autenticacao)]
):
    tokens, refresh_token = caso_de_uso.executar(dados)
    _definir_cookie_refresh(resposta, refresh_token)
    return tokens


@roteador.post(
    "/refresh",
    response_model=TokenResposta,
    status_code=status.HTTP_200_OK,
    summary="Renovar tokens de acesso",
    description=(
        "Lê o cookie HttpOnly `refresh_token`, rotaciona-o e devolve o novo "
        "access token no JSON. O navegador atualiza o cookie automaticamente."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Tokens renovados; o novo refresh token é enviado no cookie.",
            "headers": {
                "Set-Cookie": {
                    "description": "Atualiza o cookie HttpOnly `refresh_token`.",
                    "schema": {"type": "string"},
                }
            },
        }
    },
)
def renovar_tokens(
    resposta: Response,
    caso_de_uso: Annotated[
        GerenciarTokensCasoDeUso, Depends(pegar_caso_de_uso_tokens)
    ],
    refresh_token: Annotated[
        str | None,
        Cookie(
            alias="refresh_token",
            description="Cookie HttpOnly definido pelo login; enviado automaticamente pelo navegador.",
        ),
    ] = None,
):
    if refresh_token is None:
        raise CredenciaisInvalidasErro()
    tokens, novo_refresh_token = caso_de_uso.renovar(refresh_token)
    _definir_cookie_refresh(resposta, novo_refresh_token)
    return tokens


@roteador.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Encerrar a sessão atual",
    description=(
        "Revoga a sessão associada ao cookie HttpOnly `refresh_token` e remove "
        "o cookie do navegador."
    ),
)
def logout(
    resposta: Response,
    caso_de_uso: Annotated[
        GerenciarTokensCasoDeUso, Depends(pegar_caso_de_uso_tokens)
    ],
    refresh_token: Annotated[
        str | None,
        Cookie(
            alias="refresh_token",
            description="Cookie HttpOnly definido pelo login; enviado automaticamente pelo navegador.",
        ),
    ] = None,
):
    caso_de_uso.revogar_refresh_token(refresh_token)
    _limpar_cookie_refresh(resposta)
    resposta.status_code = status.HTTP_204_NO_CONTENT
    return resposta


@roteador.post(
    "/logout-todos",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Encerrar todas as sessões do usuário",
)
def logout_todos(
    usuario_atual: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        GerenciarTokensCasoDeUso, Depends(pegar_caso_de_uso_tokens)
    ],
):
    caso_de_uso.revogar_todas(usuario_atual.id)
    resposta = Response(status_code=status.HTTP_204_NO_CONTENT)
    _limpar_cookie_refresh(resposta)
    return resposta


@roteador.get(
    "/me",
    response_model=UsuarioResposta,
    summary="Obter dados do usuário logado (Disponível para todos os perfis)"
)
def obter_dados_pessoais(
    usuario_atual: Annotated[Usuario, Depends(obter_usuario_atual)]
):
    return usuario_atual


@roteador.post(
    "/me/senha",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Alterar senha do usuário autenticado",
)
def alterar_senha(
    dados: AlterarSenha,
    usuario_atual: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        AlterarSenhaCasoDeUso, Depends(pegar_caso_de_uso_alterar_senha)
    ],
):
    caso_de_uso.executar(usuario_atual, dados)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@roteador.get(
    "/",
    response_model=list[UsuarioResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar usuários com filtros e paginação (Somente Admin)"
)
def listar_usuarios(
    usuario_logado: Annotated[Usuario, Depends(apenas_admin)],
    caso_de_uso: Annotated[ListarUsuariosCasoDeUso, Depends(pegar_caso_de_uso_listar_usuarios)],
    perfil: Annotated[PerfilUsuario | None, Query(description="Filtrar por papel global (Administrador ou Membro)")] = None,
    ativo: Annotated[bool | None, Query(description="Filtrar por status")] = None,
    skip: Annotated[int, Query(ge=0, description="Número de registros para pular (Offset)")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite máximo de registros retornados (Max 100)")] = 100
):
    return caso_de_uso.executar(perfil=perfil, ativo=ativo, skip=skip, limit=limit)


def _definir_cookie_refresh(resposta: Response, token: str) -> None:
    resposta.set_cookie(
        key="refresh_token",
        value=token,
        max_age=config.dias_expiracao_refresh_token * 24 * 60 * 60,
        httponly=True,
        secure=config.refresh_cookie_secure,
        samesite=config.refresh_cookie_samesite,
        path="/usuarios",
    )


def _limpar_cookie_refresh(resposta: Response) -> None:
    resposta.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=config.refresh_cookie_secure,
        samesite=config.refresh_cookie_samesite,
        path="/usuarios",
    )