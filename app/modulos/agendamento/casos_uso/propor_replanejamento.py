from datetime import datetime, timedelta

from app.compartilhado.dominio.erros import (
    EntidadeNaoEncontradaErro,
    RegraDeNegocioErro,
)
from app.modulos.agendamento.casos_uso.reservar_horarios_aprovados import (
    ReservarHorariosAprovadosCasoDeUso,
)
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import (
    HorarioSolicitacao,
    PeriodoReserva,
    Solicitacao,
)


class ProporReplanejamentoCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        validar_periodos: ReservarHorariosAprovadosCasoDeUso,
    ):
        self.repositorio = repositorio
        self.validar_periodos = validar_periodos

    def executar(
        self,
        id_solicitacao: int,
        id_usuario: int,
        mensagem: str,
        horarios: list[HorarioSolicitacao],
        ids_recursos: list[int],
    ) -> Solicitacao:
        solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
        if solicitacao is None:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)
        periodos = [
            PeriodoReserva(
                data_hora_inicio=datetime.combine(
                    horario.data_reserva, horario.hora_inicio
                ),
                data_hora_fim=datetime.combine(
                    horario.data_reserva, horario.hora_fim
                ),
            )
            for horario in horarios
        ]
        if any(
            periodo.data_hora_fim - periodo.data_hora_inicio != timedelta(hours=1)
            or periodo.data_hora_inicio.minute != 0
            or periodo.data_hora_inicio.second != 0
            for periodo in periodos
        ):
            raise RegraDeNegocioErro(
                "As propostas devem usar horários de uma hora, iniciados em hora cheia."
            )
        self.validar_periodos.validar(
            id_espaco=solicitacao.id_espaco,
            periodos=periodos,
            ids_recursos=ids_recursos,
        )
        return self.repositorio.propor_replanejamento(
            id_solicitacao,
            id_usuario,
            mensagem.strip(),
            horarios,
            ids_recursos,
        )
