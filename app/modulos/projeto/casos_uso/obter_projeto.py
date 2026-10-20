from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import Projeto


class ObterProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, id_projeto: int) -> Projeto:
        projeto = self.repositorio.buscar_por_id(id_projeto)
        if not projeto:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        return projeto
