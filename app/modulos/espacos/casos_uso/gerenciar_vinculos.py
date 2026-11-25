from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    ConflitoDeDadosErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.usuarios.dominio.contratos import UsuarioRepositorioContrato
from app.modulos.espacos.dominio.entidades import (
    EspacoUsuarioVinculado,
    PerfilEspaco,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class GerenciarVinculosCasoDeUso:
    def __init__(
        self, 
        repo_espaco: EspacoRepositorioContrato, 
        repo_usuario: UsuarioRepositorioContrato
    ):
        self.repo_espaco = repo_espaco
        self.repo_usuario = repo_usuario

    def _validar_entidades(self, id_espaco: int, id_usuario: int):
        espaco = self.repo_espaco.buscar_por_id(id_espaco)
        if not espaco:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)

        usuario = self.repo_usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise EntidadeNaoEncontradaErro("Usuário", id_usuario)

        return espaco, usuario

    def vincular(
        self,
        id_espaco: int,
        id_usuario: int,
        perfil_espaco: PerfilEspaco,
        usuario_logado: Usuario,
    ) -> dict:
        espaco, usuario = self._validar_entidades(id_espaco, id_usuario)
        self._validar_permissao_vinculo(
            id_espaco, perfil_espaco, usuario_logado
        )

        if usuario.perfil != PerfilUsuario.MEMBRO:
            raise AcessoNegadoErro(
                "Somente membros podem receber um perfil em um espaço."
            )
        if not usuario.ativo:
            raise AcessoNegadoErro(
                "Não é possível vincular um usuário inativo a um espaço."
            )

        if self.repo_espaco.verificar_vinculo(id_espaco, id_usuario):
            raise ConflitoDeDadosErro("Este usuário já está vinculado a este espaço.")

        self.repo_espaco.adicionar_vinculo(
            id_espaco, id_usuario, perfil_espaco
        )
        return {
            "mensagem": (
                f"{perfil_espaco.value} {usuario.nome_completo} "
                f"vinculado ao espaço {espaco.nome} com sucesso."
            )
        }

    def desvincular(
        self, id_espaco: int, id_usuario: int, usuario_logado: Usuario
    ) -> dict:
        espaco, usuario = self._validar_entidades(id_espaco, id_usuario)

        eh_administrador = (
            usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR
        )
        if not eh_administrador and (
            usuario_logado.id is None
            or self.repo_espaco.obter_perfil_vinculo(
                id_espaco, usuario_logado.id
            )
            != PerfilEspaco.COORDENADOR
        ):
            raise AcessoNegadoErro(
                "Coordenadores só podem remover monitores do próprio espaço."
            )

        perfil_vinculado = self.repo_espaco.obter_perfil_vinculo(
            id_espaco, id_usuario
        )
        if not self.repo_espaco.verificar_vinculo(id_espaco, id_usuario):
            raise EntidadeNaoEncontradaErro("Vínculo", id_usuario)

        if not eh_administrador and perfil_vinculado != PerfilEspaco.MONITOR:
            raise AcessoNegadoErro(
                "Coordenadores só podem remover monitores do próprio espaço."
            )

        self.repo_espaco.remover_vinculo(id_espaco, id_usuario)
        return {
            "mensagem": (
                f"Vínculo de {usuario.nome_completo} com o espaço "
                f"{espaco.nome} removido."
            )
        }

    def listar_disponiveis(
        self, id_espaco: int, usuario_logado: Usuario
    ) -> list[EspacoUsuarioVinculado]:
        if self.repo_espaco.buscar_por_id(id_espaco) is None:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)
        if usuario_logado.perfil != PerfilUsuario.ADMINISTRADOR and (
            usuario_logado.id is None
            or self.repo_espaco.obter_perfil_vinculo(
                id_espaco, usuario_logado.id
            )
            != PerfilEspaco.COORDENADOR
        ):
            raise AcessoNegadoErro()
        return self.repo_espaco.listar_usuarios_disponiveis(id_espaco)

    def _validar_permissao_vinculo(
        self,
        id_espaco: int,
        perfil_espaco: PerfilEspaco,
        usuario_logado: Usuario,
    ) -> None:
        if usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR:
            return

        if (
            usuario_logado.id is not None
            and perfil_espaco == PerfilEspaco.MONITOR
            and self.repo_espaco.obter_perfil_vinculo(
                id_espaco, usuario_logado.id
            )
            == PerfilEspaco.COORDENADOR
        ):
            return

        raise AcessoNegadoErro(
            "Apenas administradores podem atribuir coordenadores; "
            "coordenadores só podem vincular monitores ao próprio espaço."
        )
    