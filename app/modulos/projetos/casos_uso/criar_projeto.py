from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    CredenciaisInvalidasErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.projetos.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projetos.dominio.entidade import Projeto
from app.modulos.projetos.interface.esquemas import CriarProjeto
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio


class CriarProjetoCasoDeUso:
    def __init__(
        self,
        repo_projeto: ProjetoRepositorioContrato,
        repo_usuario: UsuarioRepositorio,
    ):
        self.repo_projeto = repo_projeto
        self.repo_usuario = repo_usuario

    def executar(self, dados: CriarProjeto, usuario_logado: Usuario) -> Projeto:
        if usuario_logado.id is None:
            raise CredenciaisInvalidasErro()

        responsavel = self.repo_usuario.buscar_por_id(dados.id_responsavel)
        
        if responsavel is None:
            raise EntidadeNaoEncontradaErro("Usuário", dados.id_responsavel)

        if not self._pode_atribuir(usuario_logado, responsavel):
            raise AcessoNegadoErro(
                "Você não tem permissão para atribuir este projeto ao responsável informado."
            )

        projeto = Projeto(
            descricao=dados.descricao,
            finalidade=dados.finalidade,
            id_responsavel=dados.id_responsavel,
            id_criador=usuario_logado.id,
            quantidade_participantes=dados.quantidade_participantes,
            documentacao_base=dados.documentacao_base,
        )
        return self.repo_projeto.salvar(projeto)

    @staticmethod
    def _pode_atribuir(usuario_logado: Usuario, responsavel: Usuario) -> bool:
        mesmo_usuario = usuario_logado.id == responsavel.id
        perfil_responsavel = responsavel.perfil

        if usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR:
            return perfil_responsavel in {
                PerfilUsuario.COORDENADOR,
                PerfilUsuario.SERVIDOR,
            } or (perfil_responsavel == PerfilUsuario.ADMINISTRADOR and mesmo_usuario)

        if usuario_logado.perfil == PerfilUsuario.COORDENADOR:
            return perfil_responsavel == PerfilUsuario.SERVIDOR or (
                perfil_responsavel == PerfilUsuario.COORDENADOR and mesmo_usuario
            )

        if usuario_logado.perfil == PerfilUsuario.SERVIDOR:
            return perfil_responsavel == PerfilUsuario.SERVIDOR and mesmo_usuario

        return (
            usuario_logado.perfil == PerfilUsuario.MONITOR
            and perfil_responsavel == PerfilUsuario.SERVIDOR
        )
