from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import (
    EspacoRepositorioContrato,
    RegrasHorarioRepositorioContrato,
)
from app.modulos.espacos.dominio.entidades import EspacoHorarioFuncionamento


class ListarHorariosEspacoCasoDeUso:
    def __init__(
        self,
        repositorio_espaco: EspacoRepositorioContrato,
        repositorio_horario: RegrasHorarioRepositorioContrato,
    ):
        self.repositorio_espaco = repositorio_espaco
        self.repositorio_horario = repositorio_horario

    def executar(self, id_espaco: int) -> list[EspacoHorarioFuncionamento]:
        if self.repositorio_espaco.buscar_por_id(id_espaco) is None:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)
        return self.repositorio_horario.buscar_horarios_por_espaco(id_espaco)
