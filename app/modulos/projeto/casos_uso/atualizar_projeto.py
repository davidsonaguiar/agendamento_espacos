from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import AtualizacaoProjeto, Projeto


class AtualizarProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(
        self,
        id_projeto: int,
        id_usuario: int,
        dados: AtualizacaoProjeto,
    ) -> Projeto:
        projeto = self.repositorio.buscar_por_id(id_projeto)
        if not projeto:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        if projeto.id_responsavel != id_usuario:
            raise AcessoNegadoErro(
                "Somente o responsável pode editar os dados do projeto."
            )

        for campo in dados.model_fields_set:
            setattr(projeto, campo, getattr(dados, campo))
        return self.repositorio.atualizar(projeto)
