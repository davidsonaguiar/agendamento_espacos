from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from app.compartilhado.dominio.erros import AcessoNegadoErro, CredenciaisInvalidasErro
from app.compartilhado.infra.banco_dados import SessaoBD
from app.compartilhado.infra.config import config
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio

oauth2_esquema = HTTPBearer()

def obter_usuario_atual(
    token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_esquema)], 
    db: SessaoBD
) -> Usuario:
    try:
        payload = jwt.decode(
            token.credentials, 
            config.chave_secreta, 
            algorithms=["HS256"]
        )
        id_usuario: str = payload.get("sub")
        
        if id_usuario is None:
            raise CredenciaisInvalidasErro()
            
    except (jwt.PyJWTError, ValidationError):
        raise CredenciaisInvalidasErro()

    repositorio = UsuarioRepositorio(db)
    usuario = repositorio.buscar_por_id(int(id_usuario))
    
    if usuario is None:
        raise CredenciaisInvalidasErro("Usuário não encontrado.")
        
    if not usuario.ativo:
        raise CredenciaisInvalidasErro("Usuário inativo.")
        
    return usuario

class VerificarPerfil:
    def __init__(self, perfis_permitidos: list[PerfilUsuario]):
        self.perfis_permitidos = perfis_permitidos

    def __call__(self, usuario: Annotated[Usuario, Depends(obter_usuario_atual)]) -> Usuario:
        if usuario.perfil not in self.perfis_permitidos:
            raise AcessoNegadoErro()
        return usuario