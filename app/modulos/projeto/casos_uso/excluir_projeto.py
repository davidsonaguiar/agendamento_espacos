from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato


class ExcluirProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, id_projeto: int) -> None:
        self.repositorio.excluir(id_projeto)
