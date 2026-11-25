from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import (
    DecisaoSolicitacao,
    Solicitacao,
    StatusDecisaoSolicitacao,
)
from app.modulos.agendamento.casos_uso.decidir_solicitacao import (
    DecidirSolicitacaoCasoDeUso,
)


class ResponderPropostaCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        decidir_solicitacao: DecidirSolicitacaoCasoDeUso,
    ):
        self.repositorio = repositorio
        self.decidir_solicitacao = decidir_solicitacao

    def executar(
        self,
        id_solicitacao: int,
        id_interacao: int,
        id_usuario: int,
        aceita: bool,
        mensagem: str,
    ) -> Solicitacao:
        solicitacao = self.repositorio.responder_proposta(
            id_solicitacao,
            id_interacao,
            id_usuario,
            aceita,
            mensagem.strip(),
        )
        if not aceita:
            return solicitacao
        return self.decidir_solicitacao.executar(
            id_solicitacao,
            DecisaoSolicitacao(
                status=StatusDecisaoSolicitacao.APROVADO,
                justificativa="Proposta de replanejamento aceita pelo solicitante.",
            ),
        )
