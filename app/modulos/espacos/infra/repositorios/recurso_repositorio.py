from sqlalchemy.orm import Session

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import RecursoRepositorioContrato
from app.modulos.espacos.dominio.entidades import Recurso
from app.modulos.espacos.infra.modelos import RecursoModelo


class RecursoRepositorio(RecursoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, id_recurso: int) -> Recurso | None:
        modelo = (
            self.db.query(RecursoModelo)
            .filter(RecursoModelo.id == id_recurso)
            .first()
        )
        return self._converter(modelo) if modelo else None

    def listar_por_espaco(
        self,
        id_espaco: int,
        apenas_disponiveis: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Recurso]:
        consulta = self.db.query(RecursoModelo).filter(
            RecursoModelo.id_espaco == id_espaco
        )
        if apenas_disponiveis:
            consulta = consulta.filter(RecursoModelo.disponibilidade.is_(True))
        modelos = consulta.order_by(RecursoModelo.id).offset(skip).limit(limit).all()
        return [self._converter(modelo) for modelo in modelos]

    def salvar(self, recurso: Recurso) -> Recurso:
        modelo = RecursoModelo(
            nome=recurso.nome,
            tipo=recurso.tipo,
            autorizacao_necessaria=recurso.autorizacao_necessaria,
            disponibilidade=recurso.disponibilidade,
            reserva_independente=recurso.reserva_independente,
            id_espaco=recurso.id_espaco,
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return self._converter(modelo)

    def atualizar(self, recurso: Recurso) -> Recurso:
        if recurso.id is None:
            raise ValueError("O recurso precisa ter um ID para ser atualizado.")

        modelo = (
            self.db.query(RecursoModelo)
            .filter(RecursoModelo.id == recurso.id)
            .first()
        )
        if not modelo:
            raise EntidadeNaoEncontradaErro("Recurso", recurso.id)

        modelo.nome = recurso.nome
        modelo.tipo = recurso.tipo
        modelo.autorizacao_necessaria = recurso.autorizacao_necessaria
        modelo.disponibilidade = recurso.disponibilidade
        modelo.reserva_independente = recurso.reserva_independente
        self.db.commit()
        self.db.refresh(modelo)
        return self._converter(modelo)

    def excluir(self, id_recurso: int) -> None:
        modelo = (
            self.db.query(RecursoModelo)
            .filter(RecursoModelo.id == id_recurso)
            .first()
        )
        if not modelo:
            raise EntidadeNaoEncontradaErro("Recurso", id_recurso)

        modelo.disponibilidade = False
        self.db.commit()

    @staticmethod
    def _converter(modelo: RecursoModelo) -> Recurso:
        return Recurso(
            id=modelo.id,
            nome=modelo.nome,
            tipo=modelo.tipo,
            autorizacao_necessaria=modelo.autorizacao_necessaria,
            disponibilidade=modelo.disponibilidade,
            reserva_independente=modelo.reserva_independente,
            id_espaco=modelo.id_espaco,
        )
