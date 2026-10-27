from app.compartilhado.infra.banco_dados import SessaoBD
from app.modulos.espacos.casos_uso.atualizar_espaco import AtualizarEspacoCasoDeUso
from app.modulos.espacos.casos_uso.atualizar_horarios_espaco import (
    AtualizarHorariosEspacoCasoDeUso,
)
from app.modulos.espacos.casos_uso.cadastrar_espaco import CadastrarEspacoCasoDeUso
from app.modulos.espacos.casos_uso.desativar_espaco import DesativarEspacoCasoDeUso
from app.modulos.espacos.casos_uso.gerenciar_pausa_espaco import (
    GerenciarPausasEspacoCasoDeUso,
)
from app.modulos.espacos.casos_uso.gerenciar_recursos_espaco import (
    GerenciarRecursosEspacoCasoDeUso,
)
from app.modulos.espacos.casos_uso.gerenciar_vinculos import GerenciarVinculosCasoDeUso
from app.modulos.espacos.casos_uso.listar_espacos import ListarEspacosCasoDeUso
from app.modulos.espacos.casos_uso.reativar_espaco import ReativarEspacoCasoDeUso
from app.modulos.espacos.infra.repositorios import (
    EspacoRepositorio,
    RecursoRepositorio,
    RegrasHorarioRepositorio,
)
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio


def pegar_caso_de_uso_cadastrar_espaco(db: SessaoBD) -> CadastrarEspacoCasoDeUso:
    repositorio = EspacoRepositorio(db)
    repo_horario = RegrasHorarioRepositorio(db)
    return CadastrarEspacoCasoDeUso(repositorio, repo_horario)

def pegar_caso_de_uso_listar_espacos(db: SessaoBD) -> ListarEspacosCasoDeUso:
    return ListarEspacosCasoDeUso(EspacoRepositorio(db))

def pegar_caso_de_uso_desativar_espaco(db: SessaoBD) -> DesativarEspacoCasoDeUso:
    return DesativarEspacoCasoDeUso(EspacoRepositorio(db))

def pegar_caso_de_uso_atualizar_espaco(db: SessaoBD) -> AtualizarEspacoCasoDeUso:
    return AtualizarEspacoCasoDeUso(EspacoRepositorio(db))

def pegar_caso_de_uso_reativar_espaco(db: SessaoBD) -> ReativarEspacoCasoDeUso:
    return ReativarEspacoCasoDeUso(EspacoRepositorio(db))

def pegar_caso_de_uso_gerenciar_vinculos(db: SessaoBD) -> GerenciarVinculosCasoDeUso:
    repo_espaco = EspacoRepositorio(db)
    repo_usuario = UsuarioRepositorio(db)
    return GerenciarVinculosCasoDeUso(repo_espaco, repo_usuario)

def pegar_caso_de_uso_atualizar_horarios_espaco(db: SessaoBD) -> AtualizarHorariosEspacoCasoDeUso:
    repo_espaco = EspacoRepositorio(db)
    repo_horario = RegrasHorarioRepositorio(db)
    return AtualizarHorariosEspacoCasoDeUso(repo_espaco, repo_horario)

def pegar_caso_de_uso_gerenciar_pausas(db: SessaoBD) -> GerenciarPausasEspacoCasoDeUso:
    repo_espaco = EspacoRepositorio(db)
    repo_horario = RegrasHorarioRepositorio(db)
    return GerenciarPausasEspacoCasoDeUso(repo_espaco, repo_horario)


def pegar_caso_de_uso_gerenciar_recursos(
    db: SessaoBD,
) -> GerenciarRecursosEspacoCasoDeUso:
    return GerenciarRecursosEspacoCasoDeUso(
        EspacoRepositorio(db),
        RecursoRepositorio(db),
    )