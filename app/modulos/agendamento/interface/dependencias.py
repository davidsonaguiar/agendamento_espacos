from app.compartilhado.infra.banco_dados import SessaoBD
from app.modulos.agendamento.casos_uso.anexar_arquivo import (
    AnexarArquivoSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.cancelar_solicitacao import (
    CancelarSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.consultar_disponibilidade import (
    ConsultarDisponibilidadeCasoDeUso,
)
from app.modulos.agendamento.casos_uso.consultar_horarios_disponiveis import (
    ConsultarHorariosDisponiveisCasoDeUso,
)
from app.modulos.agendamento.casos_uso.criar_solicitacao import (
    CriarSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.decidir_solicitacao import (
    DecidirSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.listar_reservas import (
    ListarReservasCasoDeUso,
)
from app.modulos.agendamento.casos_uso.listar_solicitacoes import (
    ListarSolicitacoesCasoDeUso,
)
from app.modulos.agendamento.casos_uso.obter_solicitacao import (
    ObterSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.obter_url_anexo import (
    ObterUrlAnexoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.propor_replanejamento import (
    ProporReplanejamentoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.responder_complementacao import (
    ResponderComplementacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.responder_proposta import (
    ResponderPropostaCasoDeUso,
)
from app.modulos.agendamento.casos_uso.reservar_horarios_aprovados import (
    ReservarHorariosAprovadosCasoDeUso,
)
from app.modulos.agendamento.casos_uso.solicitar_complementacao import (
    SolicitarComplementacaoCasoDeUso,
)
from app.modulos.agendamento.infra.armazenamento_supabase import (
    ArmazenamentoSupabase,
)
from app.modulos.agendamento.infra.repositorios import (
    AgendamentoRepositorio,
    SolicitacaoRepositorio,
)
from app.modulos.espacos.infra.repositorios import (
    EspacoRepositorio,
    RegrasHorarioRepositorio,
)
from app.modulos.projetos.infra.repositorios import ProjetoRepositorio
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio


def pegar_caso_de_uso_consultar_disponibilidade(
    db: SessaoBD,
) -> ConsultarDisponibilidadeCasoDeUso:
    return ConsultarDisponibilidadeCasoDeUso(
        AgendamentoRepositorio(db),
        RegrasHorarioRepositorio(db),
    )


def pegar_caso_de_uso_consultar_horarios_disponiveis(
    db: SessaoBD,
) -> ConsultarHorariosDisponiveisCasoDeUso:
    return ConsultarHorariosDisponiveisCasoDeUso(
        AgendamentoRepositorio(db),
        RegrasHorarioRepositorio(db),
    )


def pegar_caso_de_uso_listar_reservas(
    db: SessaoBD,
) -> ListarReservasCasoDeUso:
    return ListarReservasCasoDeUso(AgendamentoRepositorio(db))


def pegar_caso_de_uso_reservar_horarios_aprovados(
    db: SessaoBD,
) -> ReservarHorariosAprovadosCasoDeUso:
    return ReservarHorariosAprovadosCasoDeUso(
        AgendamentoRepositorio(db),
        RegrasHorarioRepositorio(db),
    )


def pegar_caso_de_uso_cancelar_solicitacao(
    db: SessaoBD,
) -> CancelarSolicitacaoCasoDeUso:
    return CancelarSolicitacaoCasoDeUso(SolicitacaoRepositorio(db))


def pegar_caso_de_uso_solicitar_complementacao(
    db: SessaoBD,
) -> SolicitarComplementacaoCasoDeUso:
    return SolicitarComplementacaoCasoDeUso(SolicitacaoRepositorio(db))


def pegar_caso_de_uso_responder_complementacao(
    db: SessaoBD,
) -> ResponderComplementacaoCasoDeUso:
    return ResponderComplementacaoCasoDeUso(SolicitacaoRepositorio(db))


def pegar_caso_de_uso_propor_replanejamento(
    db: SessaoBD,
) -> ProporReplanejamentoCasoDeUso:
    return ProporReplanejamentoCasoDeUso(
        SolicitacaoRepositorio(db),
        ReservarHorariosAprovadosCasoDeUso(
            AgendamentoRepositorio(db),
            RegrasHorarioRepositorio(db),
        ),
    )


def pegar_caso_de_uso_responder_proposta(
    db: SessaoBD,
) -> ResponderPropostaCasoDeUso:
    return ResponderPropostaCasoDeUso(
        SolicitacaoRepositorio(db),
        DecidirSolicitacaoCasoDeUso(
            SolicitacaoRepositorio(db),
            ReservarHorariosAprovadosCasoDeUso(
                AgendamentoRepositorio(db),
                RegrasHorarioRepositorio(db),
            ),
        ),
    )


def pegar_caso_de_uso_criar_solicitacao(
    db: SessaoBD,
) -> CriarSolicitacaoCasoDeUso:
    return CriarSolicitacaoCasoDeUso(
        SolicitacaoRepositorio(db),
        ProjetoRepositorio(db),
        EspacoRepositorio(db),
        UsuarioRepositorio(db),
    )


def pegar_caso_de_uso_decidir_solicitacao(
    db: SessaoBD,
) -> DecidirSolicitacaoCasoDeUso:
    return DecidirSolicitacaoCasoDeUso(
        SolicitacaoRepositorio(db),
        ReservarHorariosAprovadosCasoDeUso(
            AgendamentoRepositorio(db),
            RegrasHorarioRepositorio(db),
        ),
    )


def pegar_caso_de_uso_listar_solicitacoes(
    db: SessaoBD,
) -> ListarSolicitacoesCasoDeUso:
    return ListarSolicitacoesCasoDeUso(SolicitacaoRepositorio(db))


def pegar_caso_de_uso_obter_solicitacao(
    db: SessaoBD,
) -> ObterSolicitacaoCasoDeUso:
    return ObterSolicitacaoCasoDeUso(SolicitacaoRepositorio(db))


def pegar_caso_de_uso_anexar_arquivo(
    db: SessaoBD,
) -> AnexarArquivoSolicitacaoCasoDeUso:
    return AnexarArquivoSolicitacaoCasoDeUso(
        SolicitacaoRepositorio(db),
        ArmazenamentoSupabase(),
    )


def pegar_caso_de_uso_obter_url_anexo(
    db: SessaoBD,
) -> ObterUrlAnexoCasoDeUso:
    return ObterUrlAnexoCasoDeUso(
        SolicitacaoRepositorio(db),
        ArmazenamentoSupabase(),
    )
