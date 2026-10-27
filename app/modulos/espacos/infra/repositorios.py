from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import (
    EspacoRepositorioContrato,
    RegrasHorarioRepositorioContrato,
)
from app.modulos.espacos.dominio.entidades import (
    Espaco,
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
    EspacoUsuarioVinculado,
)
from app.modulos.espacos.infra.modelos import (
    EspacoHorarioFuncionamentoModelo,
    EspacoModelo,
    EspacoPausaFuncionamentoModelo,
    espaco_usuario_tabela,
)


class EspacoRepositorio(EspacoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    @contextmanager
    def transacao(self) -> Generator[None, None, None]:
        try:
            with self.db.begin_nested():
                yield
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def buscar_por_nome(self, nome: str) -> Espaco | None:
        modelo = (
            self._consulta_com_relacionamentos()
            .filter(EspacoModelo.nome == nome)
            .first()
        )
        if not modelo:
            return None
        return self._converter(modelo)

    def listar(
        self, 
        apenas_ativos: bool = False, 
        id_usuario_vinculado: int | None = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Espaco]:
        consulta = self._consulta_com_relacionamentos()

        if id_usuario_vinculado is not None:
            consulta = consulta.join(espaco_usuario_tabela).filter(
                espaco_usuario_tabela.c.id_usuario == id_usuario_vinculado
            )

        if apenas_ativos:
            consulta = consulta.filter(EspacoModelo.disponibilidade == True)

        modelos = consulta.offset(skip).limit(limit).all()
        return [self._converter(modelo) for modelo in modelos]

    def buscar_por_id(self, id_espaco: int) -> Espaco | None:
        modelo = (
            self._consulta_com_relacionamentos()
            .filter(EspacoModelo.id == id_espaco)
            .first()
        )
        if not modelo:
            return None
        return self._converter(modelo)


    def salvar(self, espaco: Espaco) -> Espaco:
        modelo = EspacoModelo(
            nome=espaco.nome,
            descricao=espaco.descricao,
            capacidade=espaco.capacidade,
            bloco=espaco.bloco,
            disponibilidade=espaco.disponibilidade,
        )
        self.db.add(modelo)
        self.db.flush()
        self.db.refresh(modelo)
        return self._converter(modelo)

    def atualizar(self, espaco: Espaco) -> Espaco:
        modelo = (
            self._consulta_com_relacionamentos()
            .filter(EspacoModelo.id == espaco.id)
            .first()
        )
        if modelo:
            modelo.nome = espaco.nome
            modelo.descricao = espaco.descricao
            modelo.capacidade = espaco.capacidade
            modelo.bloco = espaco.bloco
            modelo.disponibilidade = espaco.disponibilidade
            
            self.db.commit()
            self.db.refresh(modelo)
            return self._converter(modelo)
        raise ValueError("Espaço não encontrado no banco de dados.")

    def _consulta_com_relacionamentos(self):
        return self.db.query(EspacoModelo).options(
            selectinload(EspacoModelo.usuarios_vinculados),
            selectinload(EspacoModelo.horarios_funcionamento),
            selectinload(EspacoModelo.pausas_funcionamento),
        )

    @staticmethod
    def _converter(modelo: EspacoModelo) -> Espaco:
        return Espaco(
            id=modelo.id,
            nome=modelo.nome,
            descricao=modelo.descricao,
            capacidade=modelo.capacidade,
            bloco=modelo.bloco,
            disponibilidade=modelo.disponibilidade,
            usuarios_vinculados=[
                EspacoUsuarioVinculado(
                    id_usuario=usuario.id,
                    nome_completo=usuario.nome_completo,
                )
                for usuario in modelo.usuarios_vinculados
            ],
            horarios_funcionamento=[
                EspacoHorarioFuncionamento.model_validate(horario)
                for horario in modelo.horarios_funcionamento
            ],
            pausas_funcionamento=[
                EspacoPausaFuncionamento.model_validate(pausa)
                for pausa in modelo.pausas_funcionamento
            ],
        )

    def verificar_vinculo(self, id_espaco: int, id_usuario: int) -> bool:
        consulta = select(espaco_usuario_tabela).where(
            espaco_usuario_tabela.c.id_espaco == id_espaco,
            espaco_usuario_tabela.c.id_usuario == id_usuario
        )
        resultado = self.db.execute(consulta).first()
        return resultado is not None

    def adicionar_vinculo(self, id_espaco: int, id_usuario: int) -> None:
        comando = espaco_usuario_tabela.insert().values(id_espaco=id_espaco, id_usuario=id_usuario)
        self.db.execute(comando)
        self.db.commit()

    def remover_vinculo(self, id_espaco: int, id_usuario: int) -> None:
        comando = espaco_usuario_tabela.delete().where(
            espaco_usuario_tabela.c.id_espaco == id_espaco,
            espaco_usuario_tabela.c.id_usuario == id_usuario
        )
        self.db.execute(comando)
        self.db.commit()


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
            raise EntidadeNaoEncontradaErro("Pausa não encontrada no banco de dados.")
    