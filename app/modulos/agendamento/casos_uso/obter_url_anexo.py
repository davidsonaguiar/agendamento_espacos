from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    CredenciaisInvalidasErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.agendamento.dominio.contratos import (
    ArmazenamentoAnexoContrato,
    SolicitacaoRepositorioContrato,
)
from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario

VALIDADE_URL_ASSINADA_SEGUNDOS = 600


class ObterUrlAnexoCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        armazenamento: ArmazenamentoAnexoContrato,
        repo_espaco: EspacoRepositorioContrato,
    ):
        self.repositorio = repositorio
        self.armazenamento = armazenamento
        self.repo_espaco = repo_espaco

    def executar(
        self, id_solicitacao: int, id_anexo: int, usuario: Usuario
    ) -> tuple[str, int]:
        if usuario.id is None:
            raise CredenciaisInvalidasErro()

        solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
        if solicitacao is None:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)
        pode_gerenciar_espaco = (
            usuario.perfil == PerfilUsuario.ADMINISTRADOR
            or (
                usuario.id is not None
                and self.repo_espaco.obter_perfil_vinculo(
                    solicitacao.id_espaco, usuario.id
                )
                == PerfilEspaco.COORDENADOR
            )
        )
        if (
            solicitacao.id_solicitante != usuario.id
            and not pode_gerenciar_espaco
        ):
            raise AcessoNegadoErro(
                "Você só pode consultar anexos das suas próprias solicitações."
            )

        anexo = self.repositorio.buscar_anexo(id_solicitacao, id_anexo)
        if anexo is None:
            raise EntidadeNaoEncontradaErro("Anexo", id_anexo)

        url = self.armazenamento.criar_url_assinada(
            anexo.url_caminho,
            VALIDADE_URL_ASSINADA_SEGUNDOS,
        )
        return url, VALIDADE_URL_ASSINADA_SEGUNDOS
