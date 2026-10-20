from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import Projeto, StatusProjeto


class AvaliarProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, id_projeto: int, status: StatusProjeto) -> Projeto:
        return self.repositorio.atualizar_status(id_projeto, status)
