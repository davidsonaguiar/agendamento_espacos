from abc import ABC, abstractmethod

from app.modulos.projeto.dominio.entidades import Projeto, StatusProjeto


class ProjetoRepositorioContrato(ABC):
    @abstractmethod
    def buscar_por_id(self, id_projeto: int) -> Projeto | None:
        pass

    @abstractmethod
    def buscar_todos(self) -> list[Projeto]:
        pass

    @abstractmethod
    def salvar(self, projeto: Projeto) -> Projeto:
        pass

    @abstractmethod
    def atualizar(self, projeto: Projeto) -> Projeto:
        pass

    @abstractmethod
    def excluir(self, id_projeto: int) -> None:
        pass

    @abstractmethod
    def verificar_participante(self, id_projeto: int, id_usuario: int) -> bool:
        pass

    @abstractmethod
    def adicionar_participante(
        self, id_projeto: int, id_usuario: int, papel_no_projeto: str
    ) -> Projeto:
        pass

    @abstractmethod
    def remover_participante(self, id_projeto: int, id_usuario: int) -> Projeto:
        pass

    @abstractmethod
    def atualizar_status(
        self, id_projeto: int, status: StatusProjeto
    ) -> Projeto:
        pass