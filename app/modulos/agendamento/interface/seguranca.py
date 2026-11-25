from typing import Annotated

from fastapi import Depends

from app.compartilhado.dominio.erros import AcessoNegadoErro
from app.compartilhado.infra.banco_dados import SessaoBD
from app.modulos.agendamento.infra.repositorios import SolicitacaoRepositorio
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from app.modulos.espacos.infra.repositorios import EspacoRepositorio
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.interface.seguranca_http import obter_usuario_atual


class VerificarGestorSolicitacao:
    def __call__(
        self,
        id_solicitacao: int,
        usuario: Annotated[Usuario, Depends(obter_usuario_atual)],
        db: SessaoBD,
    ) -> Usuario:
        if usuario.perfil == PerfilUsuario.ADMINISTRADOR:
            return usuario

        solicitacao = SolicitacaoRepositorio(db).buscar_por_id(id_solicitacao)
        if solicitacao is None:
            return usuario

        if (
            usuario.id is not None
            and EspacoRepositorio(db).obter_perfil_vinculo(
                solicitacao.id_espaco, usuario.id
            )
            == PerfilEspaco.COORDENADOR
        ):
            return usuario

        raise AcessoNegadoErro()
