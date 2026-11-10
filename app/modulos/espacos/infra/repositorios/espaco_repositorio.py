from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.espacos.dominio.entidades import (
    Espaco,
    EspacoHorarioFuncionamento,
    EspacoPausaFuncionamento,
    PerfilEspaco,
    EspacoUsuarioVinculado,
)
from app.modulos.espacos.infra.modelos import (
    EspacoModelo,
    EspacoUsuarioModelo,
    espaco_usuario_tabela,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.usuarios.infra.modelos import UsuarioModelo

from .recurso_repositorio import RecursoRepositorio
from .reservas_associadas import listar_reservas_por_espacos


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
        return self._converter_com_reservas(modelo)

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
        reservas_por_espaco, reservas_por_recurso = listar_reservas_por_espacos(
            self.db,
            [modelo.id for modelo in modelos],
        )
        return [
            self._converter(
                modelo,
                reservas_por_espaco.get(modelo.id, []),
                reservas_por_recurso,
            )
            for modelo in modelos
        ]

    def buscar_por_id(self, id_espaco: int) -> Espaco | None:
        modelo = (
            self._consulta_com_relacionamentos()
            .filter(EspacoModelo.id == id_espaco)
            .first()
        )
        if not modelo:
            return None
        return self._converter_com_reservas(modelo)


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
        return self._converter_com_reservas(modelo)

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
            return self._converter_com_reservas(modelo)
        raise ValueError("Espaço não encontrado no banco de dados.")

    def _consulta_com_relacionamentos(self):
        return self.db.query(EspacoModelo).options(
            selectinload(EspacoModelo.vinculos_usuarios).selectinload(
                EspacoUsuarioModelo.usuario
            ),
            selectinload(EspacoModelo.horarios_funcionamento),
            selectinload(EspacoModelo.pausas_funcionamento),
            selectinload(EspacoModelo.recursos),
        )

    def _converter_com_reservas(self, modelo: EspacoModelo) -> Espaco:
        reservas_por_espaco, reservas_por_recurso = listar_reservas_por_espacos(
            self.db,
            [modelo.id],
        )
        return self._converter(
            modelo,
            reservas_por_espaco.get(modelo.id, []),
            reservas_por_recurso,
        )

    @staticmethod
    def _converter(
        modelo: EspacoModelo,
        reservas=None,
        reservas_por_recurso=None,
    ) -> Espaco:
        reservas_por_recurso = reservas_por_recurso or {}
        return Espaco(
            id=modelo.id,
            nome=modelo.nome,
            descricao=modelo.descricao,
            capacidade=modelo.capacidade,
            bloco=modelo.bloco,
            disponibilidade=modelo.disponibilidade,
            usuarios_vinculados=[
                EspacoUsuarioVinculado(
                    id_usuario=vinculo.usuario.id,
                    nome_completo=vinculo.usuario.nome_completo,
                    perfil_espaco=(
                        PerfilEspaco(vinculo.perfil_espaco)
                        if vinculo.perfil_espaco is not None
                        else None
                    ),
                )
                for vinculo in modelo.vinculos_usuarios
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
                RecursoRepositorio._converter(
                    recurso,
                    reservas=reservas_por_recurso.get(recurso.id, []),
                )
                for recurso in modelo.recursos
            ],
            reservas=reservas or [],
        )

    def verificar_vinculo(self, id_espaco: int, id_usuario: int) -> bool:
        consulta = select(espaco_usuario_tabela).where(
            espaco_usuario_tabela.c.id_espaco == id_espaco,
            espaco_usuario_tabela.c.id_usuario == id_usuario
        )
        resultado = self.db.execute(consulta).first()
        return resultado is not None

    def obter_perfil_vinculo(
        self, id_espaco: int, id_usuario: int
    ) -> PerfilEspaco | None:
        consulta = select(espaco_usuario_tabela.c.perfil_espaco).where(
            espaco_usuario_tabela.c.id_espaco == id_espaco,
            espaco_usuario_tabela.c.id_usuario == id_usuario,
        )
        perfil = self.db.execute(consulta).scalar_one_or_none()
        return PerfilEspaco(perfil) if perfil is not None else None

    def listar_ids_espacos_por_perfil(
        self, id_usuario: int, perfil_espaco: PerfilEspaco
    ) -> list[int]:
        consulta = select(espaco_usuario_tabela.c.id_espaco).where(
            espaco_usuario_tabela.c.id_usuario == id_usuario,
            espaco_usuario_tabela.c.perfil_espaco == perfil_espaco.value,
        )
        return list(self.db.execute(consulta).scalars())

    def listar_usuarios_disponiveis(self, id_espaco: int) -> list[EspacoUsuarioVinculado]:
        ids_vinculados = select(espaco_usuario_tabela.c.id_usuario).where(
            espaco_usuario_tabela.c.id_espaco == id_espaco
        )
        usuarios = (
            self.db.query(UsuarioModelo)
            .filter(
                UsuarioModelo.perfil == PerfilUsuario.MEMBRO,
                UsuarioModelo.ativo.is_(True),
                ~UsuarioModelo.id.in_(ids_vinculados),
            )
            .order_by(UsuarioModelo.nome_completo)
            .all()
        )
        return [
            EspacoUsuarioVinculado(
                id_usuario=usuario.id,
                nome_completo=usuario.nome_completo,
            )
            for usuario in usuarios
        ]

    def adicionar_vinculo(
        self, id_espaco: int, id_usuario: int, perfil_espaco: PerfilEspaco
    ) -> None:
        comando = espaco_usuario_tabela.insert().values(
            id_espaco=id_espaco,
            id_usuario=id_usuario,
            perfil_espaco=perfil_espaco.value,
        )
        self.db.execute(comando)
        self.db.commit()

    def remover_vinculo(self, id_espaco: int, id_usuario: int) -> None:
        comando = espaco_usuario_tabela.delete().where(
            espaco_usuario_tabela.c.id_espaco == id_espaco,
            espaco_usuario_tabela.c.id_usuario == id_usuario
        )
        self.db.execute(comando)
        self.db.commit()
