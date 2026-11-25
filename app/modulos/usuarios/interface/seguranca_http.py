from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.compartilhado.dominio.erros import AcessoNegadoErro, CredenciaisInvalidasErro
from app.compartilhado.infra.banco_dados import SessaoBD
from app.compartilhado.infra.config import config
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.infra.repositorios import (
    SessaoAutenticacaoRepositorio,
    UsuarioRepositorio,
)

oauth2_esquema = HTTPBearer()

def obter_usuario_atual(
    token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_esquema)], 
    db: SessaoBD
) -> Usuario:
    try:
        payload = jwt.decode(
            token.credentials,
            config.chave_secreta,
            algorithms=["HS256"],
        )
        if payload.get("typ") != "access":
            raise CredenciaisInvalidasErro()
        id_usuario = int(payload["sub"])
        id_sessao = str(payload["sid"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise CredenciaisInvalidasErro()

    if not SessaoAutenticacaoRepositorio(db).sessao_ativa(id_sessao, id_usuario):
        raise CredenciaisInvalidasErro()

    repositorio = UsuarioRepositorio(db)
    usuario = repositorio.buscar_por_id(int(id_usuario))

    if usuario is None:
        raise CredenciaisInvalidasErro()

    if not usuario.ativo:
        raise CredenciaisInvalidasErro()

    return usuario

class VerificarPerfil:
    def __init__(self, perfis_permitidos: list[PerfilUsuario]):
        self.perfis_permitidos = perfis_permitidos

    def __call__(self, usuario: Annotated[Usuario, Depends(obter_usuario_atual)]) -> Usuario:
        if usuario.perfil not in self.perfis_permitidos:
            raise AcessoNegadoErro()
        return usuario