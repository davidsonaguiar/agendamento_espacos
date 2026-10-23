from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    CredenciaisInvalidasErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.solicitacao.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.solicitacao.dominio.entidades import Solicitacao
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ObterSolicitacaoCasoDeUso:
    def __init__(self, repositorio: SolicitacaoRepositorioContrato):
        self.repositorio = repositorio

    def executar(
        self, id_solicitacao: int, usuario_logado: Usuario
    ) -> Solicitacao:
        if usuario_logado.id is None:
            raise CredenciaisInvalidasErro()

        solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
        if not solicitacao:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)

        pode_consultar_todas = usuario_logado.perfil in (
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.COORDENADOR,
        )
        if (
            solicitacao.id_solicitante != usuario_logado.id
            and not pode_consultar_todas
        ):
            raise AcessoNegadoErro(
                "Você só pode consultar suas próprias solicitações."
            )

        return solicitacao
