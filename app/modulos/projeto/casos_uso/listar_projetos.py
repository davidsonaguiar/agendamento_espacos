from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import Projeto


class ListarProjetosCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self) -> list[Projeto]:
        return self.repositorio.buscar_todos()
