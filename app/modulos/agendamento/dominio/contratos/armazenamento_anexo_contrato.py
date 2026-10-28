from abc import ABC, abstractmethod


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
