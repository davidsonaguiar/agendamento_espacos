from abc import ABC, abstractmethod


class CodificadorSenhaContrato(ABC):
    @abstractmethod
    def codificar_senha(self, senha: str) -> str:
        pass

    @abstractmethod
    def verificar_senha(self, senha: str, senha_codificada: str) -> bool:
        pass
