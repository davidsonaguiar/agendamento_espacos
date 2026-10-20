from app.modulos.projeto.casos_uso.avaliar_projeto import AvaliarProjetoCasoDeUso
from app.modulos.projeto.casos_uso.atualizar_projeto import (
    AtualizarProjetoCasoDeUso,
)
from app.modulos.projeto.casos_uso.criar_projeto import CriarProjetoCasoDeUso
from app.modulos.projeto.casos_uso.excluir_projeto import ExcluirProjetoCasoDeUso
from app.modulos.projeto.casos_uso.gerenciar_participantes import (
    GerenciarParticipantesCasoDeUso,
)
from app.modulos.projeto.casos_uso.listar_projetos import ListarProjetosCasoDeUso
from app.modulos.projeto.casos_uso.obter_projeto import ObterProjetoCasoDeUso
from app.modulos.projeto.infra.repositorios import ProjetoRepositorio
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio
from app.modulos.usuarios.interface.dependencias import SessaoBD


def pegar_caso_de_uso_criar_projeto(db: SessaoBD) -> CriarProjetoCasoDeUso:
    return CriarProjetoCasoDeUso(ProjetoRepositorio(db))


def pegar_caso_de_uso_listar_projetos(db: SessaoBD) -> ListarProjetosCasoDeUso:
    return ListarProjetosCasoDeUso(ProjetoRepositorio(db))


def pegar_caso_de_uso_obter_projeto(db: SessaoBD) -> ObterProjetoCasoDeUso:
    return ObterProjetoCasoDeUso(ProjetoRepositorio(db))


def pegar_caso_de_uso_atualizar_projeto(db: SessaoBD) -> AtualizarProjetoCasoDeUso:
    return AtualizarProjetoCasoDeUso(ProjetoRepositorio(db))


def pegar_caso_de_uso_avaliar_projeto(db: SessaoBD) -> AvaliarProjetoCasoDeUso:
    return AvaliarProjetoCasoDeUso(ProjetoRepositorio(db))


def pegar_caso_de_uso_excluir_projeto(db: SessaoBD) -> ExcluirProjetoCasoDeUso:
    return ExcluirProjetoCasoDeUso(ProjetoRepositorio(db))


def pegar_caso_de_uso_gerenciar_participantes(
    db: SessaoBD,
) -> GerenciarParticipantesCasoDeUso:
    return GerenciarParticipantesCasoDeUso(
        ProjetoRepositorio(db), UsuarioRepositorio(db)
    )