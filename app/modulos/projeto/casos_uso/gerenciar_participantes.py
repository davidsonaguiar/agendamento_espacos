from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    ConflitoDeDadosErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import Projeto
from app.modulos.usuarios.dominio.contratos import UsuarioRepositorioContrato


class GerenciarParticipantesCasoDeUso:
    def __init__(
        self,
        repositorio_projeto: ProjetoRepositorioContrato,
        repositorio_usuario: UsuarioRepositorioContrato,
    ):
        self.repositorio_projeto = repositorio_projeto
        self.repositorio_usuario = repositorio_usuario

    def adicionar(
        self,
        id_projeto: int,
        id_usuario: int,
        id_solicitante: int,
        papel_no_projeto: str,
        solicitante_e_admin: bool,
    ) -> Projeto:
        projeto = self._obter_projeto(id_projeto)
        self._validar_permissao(projeto, id_solicitante, solicitante_e_admin)

        usuario = self.repositorio_usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise EntidadeNaoEncontradaErro("Usuário", id_usuario)

        if self.repositorio_projeto.verificar_participante(id_projeto, id_usuario):
            raise ConflitoDeDadosErro(
                "Este usuário já está cadastrado como participante do projeto."
            )

        return self.repositorio_projeto.adicionar_participante(
            id_projeto, id_usuario, papel_no_projeto
        )

    def remover(
        self,
        id_projeto: int,
        id_usuario: int,
        id_solicitante: int,
        solicitante_e_admin: bool,
    ) -> Projeto:
        projeto = self._obter_projeto(id_projeto)
        self._validar_permissao(projeto, id_solicitante, solicitante_e_admin)

        if not self.repositorio_projeto.verificar_participante(
            id_projeto, id_usuario
        ):
            raise EntidadeNaoEncontradaErro("Participante do projeto", id_usuario)

        return self.repositorio_projeto.remover_participante(
            id_projeto, id_usuario
        )

    def _obter_projeto(self, id_projeto: int) -> Projeto:
        projeto = self.repositorio_projeto.buscar_por_id(id_projeto)
        if not projeto:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        return projeto

    @staticmethod
    def _validar_permissao(
        projeto: Projeto, id_solicitante: int, solicitante_e_admin: bool
    ) -> None:
        if projeto.id_responsavel != id_solicitante and not solicitante_e_admin:
            raise AcessoNegadoErro(
                "Somente o responsável ou um administrador pode gerenciar participantes."
            )
