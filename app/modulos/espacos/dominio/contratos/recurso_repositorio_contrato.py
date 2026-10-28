from abc import ABC, abstractmethod

from app.modulos.espacos.dominio.entidades import Recurso


class RecursoRepositorioContrato(ABC):
    @abstractmethod
    def buscar_por_id(self, id_recurso: int) -> Recurso | None:
        pass

    @abstractmethod
    def listar_por_espaco(
        self,
        id_espaco: int,
        apenas_disponiveis: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Recurso]:
        pass

    @abstractmethod
    def salvar(self, recurso: Recurso) -> Recurso:
        pass

    @abstractmethod
    def atualizar(self, recurso: Recurso) -> Recurso:
        pass

    @abstractmethod
    def excluir(self, id_recurso: int) -> None:
        pass
