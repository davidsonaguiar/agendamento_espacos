from abc import ABC, abstractmethod

from app.modulos.espacos.dominio.entidades import (
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
)


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
