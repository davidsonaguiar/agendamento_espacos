from sqlalchemy.orm import Session, joinedload

from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.solicitacao.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.solicitacao.dominio.entidades import (
    Solicitacao,
    UsuarioEnvolvido,
)
from app.modulos.solicitacao.infra.modelos import SolicitacaoModelo
from app.modulos.usuarios.infra.modelos import UsuarioModelo


class SolicitacaoRepositorio(SolicitacaoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, id_solicitacao: int) -> Solicitacao | None:
        modelo = (
            self.db.query(SolicitacaoModelo)
            .options(joinedload(SolicitacaoModelo.usuarios_envolvidos))
            .filter(SolicitacaoModelo.id == id_solicitacao)
            .first()
        )
        return self._converter(modelo) if modelo else None

    def buscar_todas(self) -> list[Solicitacao]:
        modelos = (
            self.db.query(SolicitacaoModelo)
            .options(joinedload(SolicitacaoModelo.usuarios_envolvidos))
            .all()
        )
        return [self._converter(modelo) for modelo in modelos]

    def buscar_por_solicitante(self, id_solicitante: int) -> list[Solicitacao]:
        modelos = (
            self.db.query(SolicitacaoModelo)
            .options(joinedload(SolicitacaoModelo.usuarios_envolvidos))
            .filter(SolicitacaoModelo.id_solicitante == id_solicitante)
            .all()
        )
        return [self._converter(modelo) for modelo in modelos]

    def salvar(self, solicitacao: Solicitacao) -> Solicitacao:
        ids_usuarios = [
            usuario.id_usuario for usuario in solicitacao.usuarios_envolvidos
        ]
        usuarios = (
            self.db.query(UsuarioModelo)
            .filter(UsuarioModelo.id.in_(ids_usuarios))
            .all()
            if ids_usuarios
            else []
        )
        if len(usuarios) != len(ids_usuarios):
            ids_encontrados = {usuario.id for usuario in usuarios}
            id_inexistente = next(
                id_usuario
                for id_usuario in ids_usuarios
                if id_usuario not in ids_encontrados
            )
            raise EntidadeNaoEncontradaErro("Usuário", id_inexistente)

        modelo = SolicitacaoModelo(
            tipo=solicitacao.tipo,
            finalidade=solicitacao.finalidade,
            urgencia=solicitacao.urgencia,
            status=solicitacao.status,
            decisao_justificativa=solicitacao.decisao_justificativa,
            id_projeto=solicitacao.id_projeto,
            id_solicitante=solicitacao.id_solicitante,
            id_espaco=solicitacao.id_espaco,
            usuarios_envolvidos=usuarios,
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        solicitacao_salva = self.buscar_por_id(modelo.id)
        if solicitacao_salva is None:
            raise EntidadeNaoEncontradaErro("Solicitação", modelo.id)
        return solicitacao_salva

    @staticmethod
    def _converter(modelo: SolicitacaoModelo) -> Solicitacao:
        return Solicitacao(
            id=modelo.id,
            tipo=modelo.tipo,
            finalidade=modelo.finalidade,
            urgencia=modelo.urgencia,
            status=modelo.status,
            decisao_justificativa=modelo.decisao_justificativa,
            id_projeto=modelo.id_projeto,
            id_solicitante=modelo.id_solicitante,
            id_espaco=modelo.id_espaco,
            usuarios_envolvidos=[
                UsuarioEnvolvido(
                    id_usuario=usuario.id,
                    nome_completo=usuario.nome_completo,
                )
                for usuario in modelo.usuarios_envolvidos
            ],
        )