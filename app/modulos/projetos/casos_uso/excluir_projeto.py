from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.projetos.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ExcluirProjetoCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, id_projeto: int, usuario_logado: Usuario) -> None:
        projeto = self.repositorio.buscar_por_id(id_projeto)
        if projeto is None:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)

        eh_admin = usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR
        eh_criador = (
            usuario_logado.id is not None
            and projeto.id_criador == usuario_logado.id
        )
        if not eh_admin and not eh_criador:
            raise AcessoNegadoErro(
                "Somente o criador do projeto ou um administrador pode excluí-lo."
            )

        self.repositorio.excluir(id_projeto)
