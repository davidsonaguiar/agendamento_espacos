from abc import ABC, abstractmethod

from app.modulos.solicitacao.dominio.entidades import Solicitacao


class SolicitacaoRepositorioContrato(ABC):
    @abstractmethod
    def buscar_por_id(self, id_solicitacao: int) -> Solicitacao | None:
        pass

    @abstractmethod
    def buscar_todas(self) -> list[Solicitacao]:
        pass

    @abstractmethod
    def buscar_por_solicitante(self, id_solicitante: int) -> list[Solicitacao]:
        pass

    @abstractmethod
    def salvar(self, solicitacao: Solicitacao) -> Solicitacao:
        pass