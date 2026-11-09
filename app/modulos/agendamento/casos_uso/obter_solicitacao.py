from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    CredenciaisInvalidasErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import Solicitacao
from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ObterSolicitacaoCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        repo_espaco: EspacoRepositorioContrato,
    ):
        self.repositorio = repositorio
        self.repo_espaco = repo_espaco

    def executar(
        self, id_solicitacao: int, usuario_logado: Usuario
    ) -> Solicitacao:
        if usuario_logado.id is None:
            raise CredenciaisInvalidasErro()

        solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
        if not solicitacao:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)

        pode_gerenciar_espaco = (
            usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR
            or (
                usuario_logado.id is not None
                and self.repo_espaco.obter_perfil_vinculo(
                    solicitacao.id_espaco, usuario_logado.id
                )
                == PerfilEspaco.COORDENADOR
            )
        )
        if (
            solicitacao.id_solicitante != usuario_logado.id
            and not pode_gerenciar_espaco
        ):
            raise AcessoNegadoErro(
                "Você só pode consultar suas próprias solicitações."
            )

        return solicitacao
