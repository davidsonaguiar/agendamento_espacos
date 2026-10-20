from sqlalchemy.orm import Session, joinedload

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.projeto.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.projeto.dominio.entidades import (
    ParticipanteProjeto,
    Projeto,
    StatusProjeto,
)
from app.modulos.projeto.infra.modelos import (
    ProjetoModelo,
    ProjetoParticipanteModelo,
)


class ProjetoRepositorio(ProjetoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, id_projeto: int) -> Projeto | None:
        modelo = (
            self.db.query(ProjetoModelo)
            .options(
                joinedload(ProjetoModelo.participantes).joinedload(
                    ProjetoParticipanteModelo.usuario
                )
            )
            .filter(ProjetoModelo.id == id_projeto)
            .first()
        )
        return self._converter(modelo) if modelo else None

    def buscar_todos(self) -> list[Projeto]:
        modelos = (
            self.db.query(ProjetoModelo)
            .options(
                joinedload(ProjetoModelo.participantes).joinedload(
                    ProjetoParticipanteModelo.usuario
                )
            )
            .all()
        )
        return [self._converter(modelo) for modelo in modelos]

    def salvar(self, projeto: Projeto) -> Projeto:
        modelo = ProjetoModelo(
            descricao=projeto.descricao,
            finalidade=projeto.finalidade,
            id_responsavel=projeto.id_responsavel,
            quantidade_participantes=projeto.quantidade_participantes,
            documentacao_base=projeto.documentacao_base,
            status=projeto.status,
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return self._converter(modelo)

    def atualizar(self, projeto: Projeto) -> Projeto:
        if projeto.id is None:
            raise ValueError("O projeto precisa ter um ID para ser atualizado.")

        modelo = (
            self.db.query(ProjetoModelo)
            .filter(ProjetoModelo.id == projeto.id)
            .first()
        )
        if not modelo:
            raise EntidadeNaoEncontradaErro("Projeto", projeto.id)

        modelo.descricao = projeto.descricao
        modelo.finalidade = projeto.finalidade
        modelo.quantidade_participantes = projeto.quantidade_participantes
        modelo.documentacao_base = projeto.documentacao_base

        self.db.commit()
        projeto_atualizado = self.buscar_por_id(modelo.id)
        if projeto_atualizado is None:
            raise EntidadeNaoEncontradaErro("Projeto", modelo.id)
        return projeto_atualizado

    def excluir(self, id_projeto: int) -> None:
        modelo = (
            self.db.query(ProjetoModelo)
            .filter(ProjetoModelo.id == id_projeto)
            .first()
        )
        if not modelo:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)

        self.db.delete(modelo)
        self.db.commit()

    def verificar_participante(self, id_projeto: int, id_usuario: int) -> bool:
        return (
            self.db.query(ProjetoParticipanteModelo)
            .filter(
                ProjetoParticipanteModelo.id_projeto == id_projeto,
                ProjetoParticipanteModelo.id_usuario == id_usuario,
            )
            .first()
            is not None
        )

    def adicionar_participante(
        self, id_projeto: int, id_usuario: int, papel_no_projeto: str
    ) -> Projeto:
        self.db.add(
            ProjetoParticipanteModelo(
                id_projeto=id_projeto,
                id_usuario=id_usuario,
                papel_no_projeto=papel_no_projeto,
            )
        )
        self.db.commit()
        projeto = self.buscar_por_id(id_projeto)
        if projeto is None:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        return projeto

    def remover_participante(self, id_projeto: int, id_usuario: int) -> Projeto:
        participante = (
            self.db.query(ProjetoParticipanteModelo)
            .filter(
                ProjetoParticipanteModelo.id_projeto == id_projeto,
                ProjetoParticipanteModelo.id_usuario == id_usuario,
            )
            .first()
        )
        if not participante:
            raise EntidadeNaoEncontradaErro("Participante do projeto", id_usuario)

        self.db.delete(participante)
        self.db.commit()
        projeto = self.buscar_por_id(id_projeto)
        if projeto is None:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        return projeto

    def atualizar_status(self, id_projeto: int, status: StatusProjeto) -> Projeto:
        modelo = (
            self.db.query(ProjetoModelo)
            .filter(ProjetoModelo.id == id_projeto)
            .first()
        )
        if not modelo:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)

        modelo.status = status
        self.db.commit()
        projeto = self.buscar_por_id(id_projeto)
        if projeto is None:
            raise EntidadeNaoEncontradaErro("Projeto", id_projeto)
        return projeto

    @staticmethod
    def _converter(modelo: ProjetoModelo) -> Projeto:
        participantes = [
            ParticipanteProjeto(
                id_usuario=participante.id_usuario,
                nome_completo=participante.usuario.nome_completo,
                papel_no_projeto=participante.papel_no_projeto,
            )
            for participante in modelo.participantes
        ]
        return Projeto(
            id=modelo.id,
            descricao=modelo.descricao,
            finalidade=modelo.finalidade,
            id_responsavel=modelo.id_responsavel,
            quantidade_participantes=modelo.quantidade_participantes,
            documentacao_base=modelo.documentacao_base,
            status=modelo.status,
            participantes=participantes,
        )