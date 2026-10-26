from abc import ABC, abstractmethod
from datetime import datetime

from app.modulos.solicitacao.dominio.entidades import (
    AnexoSolicitacao,
    Solicitacao,
    StatusSolicitacao,
)


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
    def decidir(
        self,
        id_solicitacao: int,
        status: StatusSolicitacao,
        justificativa: str,
    ) -> Solicitacao:
        pass

    @abstractmethod
    def rollback(self) -> None:
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


class ArmazenamentoAnexoContrato(ABC):
    @abstractmethod
    def enviar(
        self, caminho: str, conteudo: bytes, tipo_conteudo: str
    ) -> None:
        pass

    @abstractmethod
    def remover(self, caminho: str) -> None:
        pass

    @abstractmethod
    def criar_url_assinada(
        self, caminho: str, validade_segundos: int
    ) -> str:
        pass