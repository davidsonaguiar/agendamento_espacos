from datetime import datetime

from app.compartilhado.dominio.erros import (
    ConflitoDeDadosErro,
    RegraDeNegocioErro,
)
from app.modulos.agendamento.dominio.contratos import (
    AgendamentoRepositorioContrato,
    RegrasFuncionamentoContrato,
)
from app.modulos.agendamento.dominio.entidades import PeriodoReserva


class ReservarHorariosAprovadosCasoDeUso:
    def __init__(
        self,
        repositorio: AgendamentoRepositorioContrato,
        regras_funcionamento: RegrasFuncionamentoContrato,
    ):
        self.repositorio = repositorio
        self.regras_funcionamento = regras_funcionamento

    def executar(
        self,
        id_solicitacao: int,
        id_espaco: int,
        periodos: list[PeriodoReserva],
        ids_recursos: list[int] | None = None,
    ) -> None:
        self.validar(
            id_espaco=id_espaco,
            periodos=periodos,
            ids_recursos=ids_recursos,
        )
        ids_recursos = ids_recursos or []

        periodos_ordenados = sorted(
            periodos,
            key=lambda periodo: periodo.data_hora_inicio,
        )
        self.repositorio.reservar(
            id_solicitacao,
            id_espaco,
            periodos_ordenados,
            ids_recursos,
        )

    def validar(
        self,
        id_espaco: int,
        periodos: list[PeriodoReserva],
        ids_recursos: list[int] | None = None,
    ) -> None:
        ids_recursos = ids_recursos or []
        if not periodos:
            raise RegraDeNegocioErro(
                "A solicitação não possui horários para reservar."
            )

        periodos_ordenados = sorted(
            periodos,
            key=lambda periodo: periodo.data_hora_inicio,
        )
        for indice, periodo in enumerate(periodos_ordenados):
            if periodo.data_hora_inicio <= datetime.now():
                raise ConflitoDeDadosErro(
                    "Não é possível aprovar horários que já passaram."
                )
            if indice > 0:
                anterior = periodos_ordenados[indice - 1]
                if periodo.data_hora_inicio < anterior.data_hora_fim:
                    raise ConflitoDeDadosErro(
                        "Os horários da solicitação se sobrepõem."
                    )

            motivo = self.regras_funcionamento.verificar_funcionamento(
                id_espaco,
                periodo.data_hora_inicio,
                periodo.data_hora_fim,
            )
            if motivo is not None:
                raise ConflitoDeDadosErro(
                    f"Não é possível aprovar a solicitação: {motivo}"
                )
            if self.repositorio.possui_conflito(
                id_espaco,
                periodo.data_hora_inicio,
                periodo.data_hora_fim,
                ids_recursos=ids_recursos,
                bloquear_espaco=True,
            ):
                raise ConflitoDeDadosErro(
                    "O espaço ou um dos recursos já possui uma reserva "
                    "confirmada que conflita com o período."
                )
