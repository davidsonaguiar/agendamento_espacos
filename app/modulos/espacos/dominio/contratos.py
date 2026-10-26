from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from app.modulos.espacos.dominio.entidades import (
    Espaco,
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
)


class EspacoRepositorioContrato(ABC):
    @abstractmethod
    def transacao(self) -> AbstractContextManager[None]:
        pass

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> Espaco | None:
        pass

    @abstractmethod
    def buscar_por_id(self, id_espaco: int) -> Espaco | None:
        pass

    @abstractmethod
    def listar(
        self, 
        apenas_ativos: bool = False, 
        id_usuario_vinculado: int | None = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Espaco]:
        pass

    @abstractmethod
    def salvar(self, espaco: Espaco) -> Espaco:
        pass

    @abstractmethod
    def atualizar(self, espaco: Espaco) -> Espaco:
        pass

    @abstractmethod
    def verificar_vinculo(self, id_espaco: int, id_usuario: int) -> bool:
        pass

    @abstractmethod
    def adicionar_vinculo(self, id_espaco: int, id_usuario: int) -> None:
        pass

    @abstractmethod
    def remover_vinculo(self, id_espaco: int, id_usuario: int) -> None:
        pass


class RegrasHorarioRepositorioContrato(ABC):
    @abstractmethod
    def definir_horario(self, horario: EspacoHorarioFuncionamento) -> EspacoHorarioFuncionamento:
        pass

    @abstractmethod
    def atualizar_horario(self, horario: EspacoHorarioFuncionamento) -> EspacoHorarioFuncionamento:
        pass

    @abstractmethod
    def buscar_horarios_por_espaco(self, id_espaco: int) -> list[EspacoHorarioFuncionamento]:
        pass

    @abstractmethod
    def adicionar_pausa(self, pausa: EspacoPausaFuncionamento) -> EspacoPausaFuncionamento:
        pass

    @abstractmethod
    def buscar_pausas_por_espaco(self, id_espaco: int) -> list[EspacoPausaFuncionamento]:
        pass

    @abstractmethod
    def remover_pausa(self, id_pausa: int) -> None:
        pass