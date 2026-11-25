from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import Solicitacao
from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ListarSolicitacoesCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        repo_espaco: EspacoRepositorioContrato,
    ):
        self.repositorio = repositorio
        self.repo_espaco = repo_espaco

    def executar(self, usuario_logado: Usuario) -> list[Solicitacao]:
        if usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR:
            return self.repositorio.buscar_todas()

        if usuario_logado.id is None:
            raise CredenciaisInvalidasErro()

        solicitacoes = {
            solicitacao.id: solicitacao
            for solicitacao in self.repositorio.buscar_por_solicitante(
                usuario_logado.id
            )
        }
        ids_espacos = self.repo_espaco.listar_ids_espacos_por_perfil(
            usuario_logado.id, PerfilEspaco.COORDENADOR
        )
        for solicitacao in self.repositorio.buscar_por_espacos(ids_espacos):
            solicitacoes[solicitacao.id] = solicitacao
        return list(solicitacoes.values())
