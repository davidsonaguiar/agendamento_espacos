from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.compartilhado.infra.banco_dados import Base, motor
from app.modulos.agendamento.infra.modelos import (
    ReservaAgendaModelo,
    SolicitacaoInteracaoModelo,
    agenda_reserva_recurso_tabela,
    solicitacao_recurso_tabela,
)
from app.modulos.espacos.infra.modelos import (
    EspacoHorarioFuncionamentoModelo,
    EspacoModelo,
    EspacoPausaFuncionamentoModelo,
    RecursoModelo,
    espaco_usuario_tabela,
)
from app.modulos.projetos.infra.modelos import (
    ProjetoModelo,
    ProjetoParticipanteModelo,
)
from app.modulos.agendamento.infra.modelos import (
    AnexoSolicitacaoModelo,
    SolicitacaoModelo,
    SolicitacaoHorarioModelo,
    solicitacao_usuario_tabela,
)
from app.modulos.usuarios.infra.modelos import UsuarioModelo


@asynccontextmanager
async def ciclo_de_vida_app(_: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(
        bind=motor,
        tables=[
            UsuarioModelo.__table__,
            espaco_usuario_tabela,
            EspacoModelo.__table__,
            EspacoHorarioFuncionamentoModelo.__table__,
            EspacoPausaFuncionamentoModelo.__table__,
            RecursoModelo.__table__,
            ProjetoModelo.__table__,
            ProjetoParticipanteModelo.__table__,
            SolicitacaoModelo.__table__,
            SolicitacaoHorarioModelo.__table__,
            AnexoSolicitacaoModelo.__table__,
            ReservaAgendaModelo.__table__,
            SolicitacaoInteracaoModelo.__table__,
            solicitacao_usuario_tabela,
            solicitacao_recurso_tabela,
            agenda_reserva_recurso_tabela,
        ],
    )
    yield
