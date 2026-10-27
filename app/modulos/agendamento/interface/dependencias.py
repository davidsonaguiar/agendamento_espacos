from app.compartilhado.infra.banco_dados import SessaoBD
from app.modulos.agendamento.casos_uso.cancelar_solicitacao import (
    CancelarSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.anexar_arquivo import (
    AnexarArquivoSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.criar_solicitacao import (
    CriarSolicitacaoCasoDeUso,
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
from app.modulos.agendamento.infra.armazenamento_supabase import (
    ArmazenamentoSupabase,
)
from app.modulos.agendamento.infra.repositorios import SolicitacaoRepositorio
from app.modulos.espacos.infra.repositorios import EspacoRepositorio
from app.modulos.projetos.infra.repositorios import ProjetoRepositorio
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio


def pegar_caso_de_uso_cancelar_solicitacao(
    db: SessaoBD,
) -> CancelarSolicitacaoCasoDeUso:
    return CancelarSolicitacaoCasoDeUso(SolicitacaoRepositorio(db))


def pegar_caso_de_uso_criar_solicitacao(
    db: SessaoBD,
) -> CriarSolicitacaoCasoDeUso:
    return CriarSolicitacaoCasoDeUso(
        SolicitacaoRepositorio(db),
        ProjetoRepositorio(db),
        EspacoRepositorio(db),
        UsuarioRepositorio(db),
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