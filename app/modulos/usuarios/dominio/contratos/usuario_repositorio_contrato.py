from abc import ABC, abstractmethod

from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class UsuarioRepositorioContrato(ABC):
    def listar(
        self,
        perfil: PerfilUsuario | None = None,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Usuario]:
        pass

    @abstractmethod
    def buscar_por_id(self, id_usuario: int) -> Usuario | None:
        pass

    @abstractmethod
    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        pass

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    def buscar_por_vinculo(self, vinculo_institucional: str) -> Usuario | None:
        pass

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        pass
