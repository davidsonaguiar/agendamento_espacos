from datetime import date, datetime, time, timedelta

from app.compartilhado.dominio.erros import RegraDeNegocioErro
from app.modulos.agendamento.dominio.contratos import (
    AgendamentoRepositorioContrato,
    RegrasFuncionamentoContrato,
)
from app.modulos.agendamento.dominio.entidades import PeriodoReserva


class ConsultarHorariosDisponiveisCasoDeUso:
    DURACAO_SLOT = timedelta(hours=1)
    LIMITE_DIAS = 31

    def __init__(
        self,
        agendamento_repositorio: AgendamentoRepositorioContrato,
        regras_funcionamento: RegrasFuncionamentoContrato,
    ):
        self.agendamento_repositorio = agendamento_repositorio
        self.regras_funcionamento = regras_funcionamento

    def executar(
        self,
        id_espaco: int,
        data_inicio: date,
        data_fim: date,
        ids_recursos: list[int] | None = None,
    ) -> list[PeriodoReserva]:
        if id_espaco <= 0:
            raise RegraDeNegocioErro("O ID do espaço deve ser positivo.")
        if data_fim < data_inicio:
            raise RegraDeNegocioErro(
                "A data final deve ser igual ou posterior à data inicial."
            )
        if data_inicio < date.today():
            raise RegraDeNegocioErro("A data inicial não pode estar no passado.")
        if (data_fim - data_inicio).days >= self.LIMITE_DIAS:
            raise RegraDeNegocioErro(
                f"O período consultado não pode exceder {self.LIMITE_DIAS} dias."
            )

        recursos = ids_recursos or []
        if any(id_recurso <= 0 for id_recurso in recursos):
            raise RegraDeNegocioErro("Os IDs dos recursos devem ser positivos.")
        if len(recursos) != len(set(recursos)):
            raise RegraDeNegocioErro("Não informe recursos duplicados.")
        self.agendamento_repositorio.validar_recursos(id_espaco, recursos)

        horarios = [
            horario
            for horario in self.regras_funcionamento.buscar_horarios_por_espaco(
                id_espaco
            )
            if horario.ativo
        ]
        pausas = self.regras_funcionamento.buscar_pausas_por_espaco(id_espaco)

        inicio_periodo = datetime.combine(data_inicio, time.min)
        fim_periodo = datetime.combine(data_fim + timedelta(days=1), time.min)
        mensagem = self.regras_funcionamento.verificar_funcionamento(
            id_espaco,
            inicio_periodo,
            inicio_periodo + self.DURACAO_SLOT,
        )
        if mensagem == "O espaço está desativado.":
            return []

        reservas = self.agendamento_repositorio.listar(
            inicio_periodo,
            fim_periodo,
        )
        disponiveis: list[PeriodoReserva] = []
        horarios_adicionados: set[datetime] = set()
        dia_atual = data_inicio
        while dia_atual <= data_fim:
            if not any(
                pausa.data_inicio <= dia_atual <= pausa.data_fim for pausa in pausas
            ):
                dia_semana = (dia_atual.weekday() + 1) % 7
                horarios_do_dia = [
                    horario
                    for horario in horarios
                    if horario.dia_semana == dia_semana
                ]
                for horario in horarios_do_dia:
                    inicio_slot = datetime.combine(dia_atual, horario.hora_abertura)
                    fechamento = datetime.combine(
                        dia_atual, horario.hora_fechamento
                    )
                    while inicio_slot + self.DURACAO_SLOT <= fechamento:
                        fim_slot = inicio_slot + self.DURACAO_SLOT
                        conflito = any(
                            reserva.data_hora_inicio < fim_slot
                            and reserva.data_hora_fim > inicio_slot
                            and (
                                reserva.id_espaco == id_espaco
                                or not recursos
                                or set(recursos).intersection(reserva.ids_recursos)
                            )
                            for reserva in reservas
                        )
                        if not conflito and inicio_slot not in horarios_adicionados:
                            disponiveis.append(
                                PeriodoReserva(
                                    data_hora_inicio=inicio_slot,
                                    data_hora_fim=fim_slot,
                                )
                            )
                            horarios_adicionados.add(inicio_slot)
                        inicio_slot += self.DURACAO_SLOT
            dia_atual += timedelta(days=1)
        return disponiveis
