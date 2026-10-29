from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    ConflitoDeDadosErro,
    EntidadeNaoEncontradaErro,
)
from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.usuarios.dominio.contratos import UsuarioRepositorioContrato
from app.modulos.usuarios.dominio.entidades import PerfilUsuario


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

        if usuario.perfil not in [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR, PerfilUsuario.MONITOR]:
            raise AcessoNegadoErro("Apenas usuários com perfil de Coordenador ou Monitor podem ser vinculados a espaços.")
        
        return espaco, usuario


    def vincular(self, id_espaco: int, id_usuario: int) -> dict:
        espaco, usuario = self._validar_entidades(id_espaco, id_usuario)

        if self.repo_espaco.verificar_vinculo(id_espaco, id_usuario):
            raise ConflitoDeDadosErro("Este usuário já está vinculado a este espaço.")

        self.repo_espaco.adicionar_vinculo(id_espaco, id_usuario)
        return {"mensagem": f"{usuario.perfil.value} {usuario.nome_completo} vinculado ao espaço {espaco.nome} com sucesso."}

    
    def desvincular(self, id_espaco: int, id_usuario: int) -> dict:
        espaco, usuario = self._validar_entidades(id_espaco, id_usuario)

        if not self.repo_espaco.verificar_vinculo(id_espaco, id_usuario):
            raise EntidadeNaoEncontradaErro("Vínculo", id_usuario)

        self.repo_espaco.remover_vinculo(id_espaco, id_usuario)
        return {"mensagem": f"Vínculo do {usuario.perfil.value} {usuario.nome_completo} com o espaço {espaco.nome} removido."}
    