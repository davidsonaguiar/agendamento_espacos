from typing import Annotated

from fastapi import Depends

from app.compartilhado.dominio.erros import AcessoNegadoErro
from app.compartilhado.infra.banco_dados import SessaoBD
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from app.modulos.espacos.infra.repositorios import EspacoRepositorio
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import obter_usuario_atual


class VerificarPerfilEspaco:
    def __init__(self, perfis_permitidos: list[PerfilEspaco]):
        self.perfis_permitidos = perfis_permitidos

    def __call__(
        self,
        id_espaco: int,
        usuario: Annotated[Usuario, Depends(obter_usuario_atual)],
        db: SessaoBD,
    ) -> Usuario:
        if usuario.perfil == PerfilUsuario.ADMINISTRADOR:
            return usuario

        if (
            usuario.id is not None
            and EspacoRepositorio(db).obter_perfil_vinculo(
                id_espaco, usuario.id
            )
            in self.perfis_permitidos
        ):
            return usuario

        raise AcessoNegadoErro()
