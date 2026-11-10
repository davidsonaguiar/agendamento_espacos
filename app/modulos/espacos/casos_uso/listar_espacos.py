from app.modulos.espacos.dominio.entidades import Espaco
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class ListarEspacosCasoDeUso:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def executar(
        self, usuario_logado: Usuario, skip: int = 0, limit: int = 100
    ) -> list[Espaco]:
        if usuario_logado.perfil == PerfilUsuario.ADMINISTRADOR:
            return self.repositorio.listar(skip=skip, limit=limit)

        if usuario_logado.perfil == PerfilUsuario.MEMBRO:
            return self.repositorio.listar(apenas_ativos=True, skip=skip, limit=limit)
        return []
