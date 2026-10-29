from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.espacos.dominio.entidades import (
    Espaco,
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
    EspacoUsuarioVinculado,
)
from app.modulos.espacos.infra.modelos import EspacoModelo, espaco_usuario_tabela

from .recurso_repositorio import RecursoRepositorio


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
            selectinload(EspacoModelo.recursos),
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
            recursos=[
                RecursoRepositorio._converter(recurso)
                for recurso in modelo.recursos
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
