from app.compartilhado.dominio.erros import RegraDeNegocioErro
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import Solicitacao


class SolicitarComplementacaoCasoDeUso:
    def __init__(self, repositorio: SolicitacaoRepositorioContrato):
        self.repositorio = repositorio

    def executar(
        self, id_solicitacao: int, id_usuario: int, mensagem: str
    ) -> Solicitacao:
        mensagem = mensagem.strip()
        if len(mensagem) < 3:
            raise RegraDeNegocioErro(
                "A mensagem deve conter ao menos 3 caracteres."
            )
        return self.repositorio.solicitar_complementacao(
            id_solicitacao, id_usuario, mensagem
        )
