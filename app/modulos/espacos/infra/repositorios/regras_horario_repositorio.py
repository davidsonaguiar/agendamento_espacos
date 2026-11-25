from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import RegrasHorarioRepositorioContrato
from app.modulos.espacos.dominio.entidades import (
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
)
from app.modulos.espacos.infra.modelos import (
    EspacoModelo,
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

    def verificar_funcionamento(
        self,
        id_espaco: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
    ) -> str | None:
        espaco = (
            self.db.query(EspacoModelo)
            .filter(EspacoModelo.id == id_espaco)
            .first()
        )
        if espaco is None:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)
        if not espaco.disponibilidade:
            return "O espaço está desativado."

        primeiro_dia = data_hora_inicio.date()
        ultimo_dia = data_hora_fim.date()
        if data_hora_fim.time() == time.min and ultimo_dia > primeiro_dia:
            ultimo_dia -= timedelta(days=1)

        pausas = self.buscar_pausas_por_espaco(id_espaco)
        horarios_por_dia: dict[int, list[EspacoHorarioFuncionamento]] = {}
        for horario in self.buscar_horarios_por_espaco(id_espaco):
            if horario.ativo:
                horarios_por_dia.setdefault(horario.dia_semana, []).append(horario)

        dia_atual = primeiro_dia
        while dia_atual <= ultimo_dia:
            if any(
                pausa.data_inicio <= dia_atual <= pausa.data_fim
                for pausa in pausas
            ):
                return f"O espaço está fechado em {dia_atual.isoformat()}."

            inicio_dia = max(
                data_hora_inicio,
                datetime.combine(dia_atual, time.min),
            )
            fim_dia = min(
                data_hora_fim,
                datetime.combine(dia_atual + timedelta(days=1), time.min),
            )
            dia_semana = (dia_atual.weekday() + 1) % 7
            horarios = horarios_por_dia.get(dia_semana, [])
            esta_no_horario = any(
                inicio_dia >= datetime.combine(dia_atual, horario.hora_abertura)
                and fim_dia <= datetime.combine(dia_atual, horario.hora_fechamento)
                for horario in horarios
            )
            if not esta_no_horario:
                return (
                    "O período solicitado está fora do horário de funcionamento "
                    f"em {dia_atual.isoformat()}."
                )
            dia_atual += timedelta(days=1)

        return None

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
