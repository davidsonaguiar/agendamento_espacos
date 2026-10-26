from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modulos.agendamento.casos_uso.consultar_disponibilidade import (
    ConsultarDisponibilidadeCasoDeUso,
)
from app.modulos.agendamento.casos_uso.listar_reservas import (
    ListarReservasCasoDeUso,
)
from app.modulos.agendamento.dominio.entidades import ReservaAgenda
from app.modulos.agendamento.interface.dependencias import (
    pegar_caso_de_uso_consultar_disponibilidade,
    pegar_caso_de_uso_listar_reservas,
)
from app.modulos.agendamento.interface.esquemas import (
    DisponibilidadeReservaResposta,
    ReservaAgendaResposta,
)
from app.modulos.usuarios.dominio.entidades import Usuario
from app.modulos.usuarios.interface.seguranca_http import obter_usuario_atual

roteador = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])


@roteador.get(
    "/disponibilidade",
    response_model=DisponibilidadeReservaResposta,
    status_code=status.HTTP_200_OK,
    summary="Consultar disponibilidade de um espaço em um período",
)
def consultar_disponibilidade(
    id_espaco: int,
    data_hora_inicio: datetime,
    data_hora_fim: datetime,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ConsultarDisponibilidadeCasoDeUso,
        Depends(pegar_caso_de_uso_consultar_disponibilidade),
    ],
) -> DisponibilidadeReservaResposta:
    disponivel, motivo = caso_de_uso.executar(
        id_espaco,
        data_hora_inicio,
        data_hora_fim,
    )
    return DisponibilidadeReservaResposta(
        id_espaco=id_espaco,
        data_hora_inicio=data_hora_inicio,
        data_hora_fim=data_hora_fim,
        disponivel=disponivel,
        motivo=motivo,
    )


@roteador.get(
    "/",
    response_model=list[ReservaAgendaResposta],
    status_code=status.HTTP_200_OK,
    summary="Consultar reservas confirmadas em um período",
)
def listar_reservas(
    data_hora_inicio: datetime,
    data_hora_fim: datetime,
    usuario_logado: Annotated[Usuario, Depends(obter_usuario_atual)],
    caso_de_uso: Annotated[
        ListarReservasCasoDeUso,
        Depends(pegar_caso_de_uso_listar_reservas),
    ],
    id_espaco: int | None = None,
) -> list[ReservaAgenda]:
    return caso_de_uso.executar(
        data_hora_inicio,
        data_hora_fim,
        id_espaco,
    )
