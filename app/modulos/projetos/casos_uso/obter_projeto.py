from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.projetos.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projetos.dominio.entidade import Projeto
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ObterProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, id_projeto: int, usuario: Usuario) -> Projeto:
        if usuario.perfil == PerfilUsuario.MEMBRO:
            projeto = (
                self.repositorio.buscar_por_id_vinculado(
                    id_projeto,
                    usuario.id,
                    incluir_responsabilidade=True,
                )
                if usuario.id is not None
                else None
            )
        else:
            projeto = self.repositorio.buscar_por_id(id_projeto)
        if not projeto:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        return projeto
