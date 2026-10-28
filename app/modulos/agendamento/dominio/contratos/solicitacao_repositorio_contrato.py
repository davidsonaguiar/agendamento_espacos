from abc import ABC, abstractmethod
from datetime import datetime

from app.modulos.agendamento.dominio.entidades import AnexoSolicitacao, Solicitacao


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

    @abstractmethod
    def cancelar(self, id_solicitacao: int) -> Solicitacao | None:
        pass

    @abstractmethod
    def buscar_anexo(
        self, id_solicitacao: int, id_anexo: int
    ) -> AnexoSolicitacao | None:
        pass

    @abstractmethod
    def salvar_anexo(
        self,
        id_solicitacao: int,
        nome_arquivo: str,
        url_caminho: str,
        tipo_arquivo: str,
        data_upload: datetime,
    ) -> AnexoSolicitacao:
        pass
