from abc import ABC, abstractmethod


class TokenContrato(ABC):
    @abstractmethod
    def criar_token_acesso(self, id_usuario: int) -> str:
        pass
