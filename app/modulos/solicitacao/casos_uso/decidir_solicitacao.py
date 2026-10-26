from datetime import datetime

from app.compartilhado.dominio.erros import (
    ConflitoDeDadosErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.agendamento.casos_uso.reservar_horarios_aprovados import (
    ReservarHorariosAprovadosCasoDeUso,
)
from app.modulos.agendamento.dominio.entidades import PeriodoReserva
from app.modulos.solicitacao.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.solicitacao.dominio.entidades import (
    DecisaoSolicitacao,
    Solicitacao,
    StatusSolicitacao,
)


class DecidirSolicitacaoCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        reservar_horarios: ReservarHorariosAprovadosCasoDeUso,
    ):
        self.repositorio = repositorio
        self.reservar_horarios = reservar_horarios

    def executar(
        self,
        id_solicitacao: int,
        decisao: DecisaoSolicitacao,
    ) -> Solicitacao:
        try:
            solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
            if solicitacao is None:
                raise EntidadeNaoEncontradaErro(
                    "Solicitação", id_solicitacao
                )
            if solicitacao.status != StatusSolicitacao.PENDENTE.value:
                raise ConflitoDeDadosErro(
                    "Somente solicitações pendentes podem receber decisão."
                )

            status = StatusSolicitacao(decisao.status.value)
            if status == StatusSolicitacao.APROVADO:
                periodos = [
                    PeriodoReserva(
                        data_hora_inicio=datetime.combine(
                            horario.data_reserva,
                            horario.hora_inicio,
                        ),
                        data_hora_fim=datetime.combine(
                            horario.data_reserva,
                            horario.hora_fim,
                        ),
                    )
                    for horario in solicitacao.horarios
                ]
                self.reservar_horarios.executar(
                    id_solicitacao=id_solicitacao,
                    id_espaco=solicitacao.id_espaco,
                    periodos=periodos,
                )

            return self.repositorio.decidir(
                id_solicitacao=id_solicitacao,
                status=status,
                justificativa=decisao.justificativa,
            )
        except Exception:
            self.repositorio.rollback()
            raise
