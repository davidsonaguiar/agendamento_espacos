from app.modulos.agendamento.casos_uso.consultar_disponibilidade import (
    ConsultarDisponibilidadeCasoDeUso,
)
from app.modulos.agendamento.casos_uso.listar_reservas import (
    ListarReservasCasoDeUso,
)
from app.modulos.agendamento.casos_uso.reservar_horarios_aprovados import (
    ReservarHorariosAprovadosCasoDeUso,
)
from app.modulos.agendamento.infra.repositorios import AgendamentoRepositorio
from app.modulos.espacos.infra.repositorios import RegrasHorarioRepositorio
from app.modulos.usuarios.interface.dependencias import SessaoBD


def pegar_caso_de_uso_consultar_disponibilidade(
    db: SessaoBD,
) -> ConsultarDisponibilidadeCasoDeUso:
    return ConsultarDisponibilidadeCasoDeUso(
        AgendamentoRepositorio(db),
        RegrasHorarioRepositorio(db),
    )


def pegar_caso_de_uso_listar_reservas(db: SessaoBD) -> ListarReservasCasoDeUso:
    return ListarReservasCasoDeUso(AgendamentoRepositorio(db))


def pegar_caso_de_uso_reservar_horarios_aprovados(
    db: SessaoBD,
) -> ReservarHorariosAprovadosCasoDeUso:
    return ReservarHorariosAprovadosCasoDeUso(
        AgendamentoRepositorio(db),
        RegrasHorarioRepositorio(db),
    )
