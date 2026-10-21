from app.modulos.projetos.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projetos.dominio.entidade import Projeto
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ListarProjetosCasoDeUso:
    def __init__(self, repositorio: ProjetoRepositorioContrato):
        self.repositorio = repositorio

    def executar(self, usuario: Usuario) -> list[Projeto]:
        if usuario.perfil in {PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO}:
            if usuario.id is None:
                return []
            return self.repositorio.buscar_vinculados_a_usuario(
                usuario.id,
                incluir_responsabilidade=usuario.perfil == PerfilUsuario.SERVIDOR,
            )
        return self.repositorio.buscar_todos()
