from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    ConflitoDeDadosErro,
    CredenciaisInvalidasErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import (
    Solicitacao,
    StatusSolicitacao,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class CancelarSolicitacaoCasoDeUso:
    def __init__(self, repositorio: SolicitacaoRepositorioContrato):
        self.repositorio = repositorio

    def executar(
        self, id_solicitacao: int, usuario_logado: Usuario
    ) -> Solicitacao:
        if usuario_logado.id is None:
            raise CredenciaisInvalidasErro()

        solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
        if solicitacao is None:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)

        eh_criador = solicitacao.id_solicitante == usuario_logado.id
        eh_administrador = usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR
        if not eh_criador and not eh_administrador:
            raise AcessoNegadoErro(
                "Somente o criador da solicitação ou um administrador pode "
                "cancelá-la."
            )

        if solicitacao.status != StatusSolicitacao.PENDENTE.value:
            raise ConflitoDeDadosErro(
                "Somente solicitações pendentes podem ser canceladas."
            )

        solicitacao_cancelada = self.repositorio.cancelar(id_solicitacao)
        if solicitacao_cancelada is None:
            raise ConflitoDeDadosErro(
                "A solicitação não está mais pendente e não pode ser cancelada."
            )
        return solicitacao_cancelada
