from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import NovoProjeto, Projeto


class CriarProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, dados: NovoProjeto, id_responsavel: int) -> Projeto:
        projeto = Projeto(
            descricao=dados.descricao,
            finalidade=dados.finalidade,
            id_responsavel=id_responsavel,
            quantidade_participantes=dados.quantidade_participantes,
            documentacao_base=dados.documentacao_base,
        )
        return self.repositorio.salvar(projeto)
