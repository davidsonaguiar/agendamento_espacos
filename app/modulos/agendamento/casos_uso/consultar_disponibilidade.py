from datetime import datetime

from app.compartilhado.dominio.erros import RegraDeNegocioErro
from app.modulos.agendamento.dominio.contratos import (
    AgendamentoRepositorioContrato,
    RegrasFuncionamentoContrato,
)


class ConsultarDisponibilidadeCasoDeUso:
    def __init__(
        self,
        repositorio: AgendamentoRepositorioContrato,
        regras_funcionamento: RegrasFuncionamentoContrato,
    ):
        self.repositorio = repositorio
        self.regras_funcionamento = regras_funcionamento

    def executar(
        self,
        id_espaco: int | None,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        ids_recursos: list[int] | None = None,
    ) -> tuple[bool, str | None, int, bool]:
        espaco_reservado = id_espaco is not None
        recursos = ids_recursos or []
        if len(recursos) != len(set(recursos)):
            raise RegraDeNegocioErro("Não informe recursos duplicados.")
        if id_espaco is None:
            id_espaco = self.repositorio.buscar_id_espaco_dos_recursos(recursos)

        if (
            data_hora_inicio.tzinfo is not None
            or data_hora_fim.tzinfo is not None
        ):
            raise RegraDeNegocioErro(
                "Informe data e hora locais sem deslocamento de fuso horário."
            )
        if data_hora_inicio >= data_hora_fim:
            raise RegraDeNegocioErro("O fim do período deve ser posterior ao início.")
        if data_hora_inicio <= datetime.now():
            raise RegraDeNegocioErro("O início do período deve ser futuro.")

        motivo = self.regras_funcionamento.verificar_funcionamento(
            id_espaco,
            data_hora_inicio,
            data_hora_fim,
        )
        if motivo is not None:
            return False, motivo, id_espaco, espaco_reservado
        if self.repositorio.possui_conflito(
            id_espaco,
            data_hora_inicio,
            data_hora_fim,
            bloquear_espaco=espaco_reservado,
            ids_recursos=recursos,
        ):
            return (
                False,
                "O espaço já possui uma reserva confirmada que conflita "
                "com o período solicitado.",
                id_espaco,
                espaco_reservado,
            )
        return True, None, id_espaco, espaco_reservado
