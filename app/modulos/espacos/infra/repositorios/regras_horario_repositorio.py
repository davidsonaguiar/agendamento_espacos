from sqlalchemy.orm import Session

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import RegrasHorarioRepositorioContrato
from app.modulos.espacos.dominio.entidades import (
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
)
from app.modulos.espacos.infra.modelos import (
    EspacoHorarioFuncionamentoModelo,
    EspacoPausaFuncionamentoModelo,
)


class RegrasHorarioRepositorio(RegrasHorarioRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def definir_horario(self, horario: EspacoHorarioFuncionamento) -> EspacoHorarioFuncionamento:
        modelo = EspacoHorarioFuncionamentoModelo(
            dia_semana=horario.dia_semana,
            hora_abertura=horario.hora_abertura,
            hora_fechamento=horario.hora_fechamento,
            ativo=horario.ativo,
            id_espaco=horario.id_espaco
        )
        self.db.add(modelo)
        self.db.flush()
        self.db.refresh(modelo)
        return EspacoHorarioFuncionamento.model_validate(modelo)

    def atualizar_horario(self, horario: EspacoHorarioFuncionamento) -> EspacoHorarioFuncionamento:
        modelo = self.db.query(EspacoHorarioFuncionamentoModelo).filter(
            EspacoHorarioFuncionamentoModelo.id_espaco == horario.id_espaco,
            EspacoHorarioFuncionamentoModelo.dia_semana == horario.dia_semana
        ).first()
        
        if modelo:
            modelo.hora_abertura = horario.hora_abertura
            modelo.hora_fechamento = horario.hora_fechamento
            modelo.ativo = horario.ativo
            
            self.db.commit()
            self.db.refresh(modelo)
            return EspacoHorarioFuncionamento.model_validate(modelo)
            
        raise ValueError("Horário não encontrado para este dia e espaço.")

    def buscar_horarios_por_espaco(self, id_espaco: int) -> list[EspacoHorarioFuncionamento]:
        modelos = self.db.query(EspacoHorarioFuncionamentoModelo).filter(
            EspacoHorarioFuncionamentoModelo.id_espaco == id_espaco
        ).order_by(EspacoHorarioFuncionamentoModelo.dia_semana).all()
        
        return [EspacoHorarioFuncionamento.model_validate(m) for m in modelos]

    def adicionar_pausa(self, pausa: EspacoPausaFuncionamento) -> EspacoPausaFuncionamento:
        modelo = EspacoPausaFuncionamentoModelo(
            data_inicio=pausa.data_inicio,
            data_fim=pausa.data_fim,
            motivo=pausa.motivo,
            id_espaco=pausa.id_espaco
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return EspacoPausaFuncionamento.model_validate(modelo)

    def buscar_pausas_por_espaco(self, id_espaco: int) -> list[EspacoPausaFuncionamento]:
        modelos = self.db.query(EspacoPausaFuncionamentoModelo).filter(
            EspacoPausaFuncionamentoModelo.id_espaco == id_espaco
        ).all()
        return [EspacoPausaFuncionamento.model_validate(m) for m in modelos]

    def remover_pausa(self, id_pausa: int) -> None:
        modelo = self.db.query(EspacoPausaFuncionamentoModelo).filter(
            EspacoPausaFuncionamentoModelo.id == id_pausa
        ).first()
        
        if modelo:
            self.db.delete(modelo)
            self.db.commit()
        else:
            raise EntidadeNaoEncontradaErro("Pausa de funcionamento", id_pausa)
