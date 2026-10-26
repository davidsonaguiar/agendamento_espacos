from datetime import datetime

from app.compartilhado.dominio.erros import RegraDeNegocioErro
from app.modulos.agendamento.dominio.contratos import AgendamentoRepositorioContrato
from app.modulos.agendamento.dominio.entidades import ReservaAgenda


class ListarReservasCasoDeUso:
    def __init__(self, repositorio: AgendamentoRepositorioContrato):
        self.repositorio = repositorio

    def executar(
        self,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        id_espaco: int | None = None,
    ) -> list[ReservaAgenda]:
        if data_hora_inicio.tzinfo is not None or data_hora_fim.tzinfo is not None:
            raise RegraDeNegocioErro(
                "Informe data e hora locais sem deslocamento de fuso horário."
            )
        if data_hora_inicio >= data_hora_fim:
            raise RegraDeNegocioErro("O fim do período deve ser posterior ao início.")
        if id_espaco is not None and id_espaco <= 0:
            raise RegraDeNegocioErro("O ID do espaço deve ser positivo.")
        return self.repositorio.listar(
            data_hora_inicio,
            data_hora_fim,
            id_espaco,
        )
