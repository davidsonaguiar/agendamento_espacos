from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.modulos.usuarios.casos_uso.autenticar_usuario import AutenticarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.cadastrar_usuario import CadastrarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.listar_usuarios import ListarUsuariosCasoDeUso
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.dependencias import (
    pegar_caso_de_uso_autenticacao,
    pegar_caso_de_uso_cadastro,
    pegar_caso_de_uso_listar_usuarios,
)
from app.modulos.usuarios.interface.esquemas import (
    CriarServidor,
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
admin_ou_coordenador = VerificarPerfil([PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR])

@roteador.post(
    "/servidor",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo Servidor Solicitante (Público)"
)
def cadastrar_servidor(
    dados: CriarServidor,
    caso_de_uso: Annotated[CadastrarUsuarioCasoDeUso, Depends(pegar_caso_de_uso_cadastro)]
):
    return caso_de_uso.servidor(dados)


@roteador.post(
    "/interno",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuários internos (Somente Admin e Coordenador)"
)
def cadastrar_usuario_interno(
    dados: CriarUsuarioInterno,
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[CadastrarUsuarioCasoDeUso, Depends(pegar_caso_de_uso_cadastro)]
):
    return caso_de_uso.interno(dados, usuario_logado)


@roteador.post(
    "/login",
    response_model=TokenResposta,
    status_code=status.HTTP_200_OK,
    summary="Autenticar Usuário - Login (Público)",
    description="Valida as credenciais do usuário e devolve o token JWT de acesso. (Público)"
)
def login(
    dados: UsuarioLogin,
    caso_de_uso: Annotated[AutenticarUsuarioCasoDeUso, Depends(pegar_caso_de_uso_autenticacao)]
):
    return caso_de_uso.executar(dados)


@roteador.get(
    "/me",
    response_model=UsuarioResposta,
    summary="Obter dados do usuário logado (Disponível para todos os perfis)"
)
def obter_dados_pessoais(
    usuario_atual: Annotated[Usuario, Depends(obter_usuario_atual)]
):
    return usuario_atual


@roteador.get(
    "/",
    response_model=list[UsuarioResposta],
    status_code=status.HTTP_200_OK,
    summary="Listar usuários com filtros e paginação (Público)"
)
def listar_usuarios(
    usuario_logado: Annotated[Usuario, Depends(admin_ou_coordenador)],
    caso_de_uso: Annotated[ListarUsuariosCasoDeUso, Depends(pegar_caso_de_uso_listar_usuarios)],
    perfil: Annotated[PerfilUsuario | None, Query(description="Filtrar por perfil (Admin, Coordenador, etc)")] = None,
    ativo: Annotated[bool | None, Query(description="Filtrar por status")] = None,
    skip: Annotated[int, Query(ge=0, description="Número de registros para pular (Offset)")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite máximo de registros retornados (Max 100)")] = 100
):
    return caso_de_uso.executar(perfil=perfil, ativo=ativo, skip=skip, limit=limit)