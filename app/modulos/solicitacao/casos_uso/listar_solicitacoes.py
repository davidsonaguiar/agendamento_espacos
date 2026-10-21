from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.modulos.solicitacao.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.solicitacao.dominio.entidades import Solicitacao
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ListarSolicitacoesCasoDeUso:
    def __init__(self, repositorio: SolicitacaoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, usuario_logado: Usuario) -> list[Solicitacao]:
        if usuario_logado.perfil in (
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.COORDENADOR,
        ):
            return self.repositorio.buscar_todas()

        if usuario_logado.id is None:
            raise CredenciaisInvalidasErro()
        return self.repositorio.buscar_por_solicitante(usuario_logado.id)
