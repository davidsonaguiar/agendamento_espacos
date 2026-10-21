from app.modulos.espacos.infra.repositorios import EspacoRepositorio
from app.modulos.projetos.infra.repositorios import ProjetoRepositorio
from app.modulos.solicitacao.casos_uso.criar_solicitacao import (
    CriarSolicitacaoCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.listar_solicitacoes import (
    ListarSolicitacoesCasoDeUso,
)
from app.modulos.solicitacao.casos_uso.obter_solicitacao import (
    ObterSolicitacaoCasoDeUso,
)
from app.modulos.solicitacao.infra.repositorios import SolicitacaoRepositorio
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio
from app.modulos.usuarios.interface.dependencias import SessaoBD


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