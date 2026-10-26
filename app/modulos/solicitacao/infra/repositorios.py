from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.compartilhado.dominio.erros import (
    ConflitoDeDadosErro,
    EntidadeNaoEncontradaErro,
    FalhaPersistenciaErro,
)
from app.modulos.solicitacao.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.solicitacao.dominio.entidades import (
    AnexoSolicitacao,
    HorarioSolicitacao,
    Solicitacao,
    StatusSolicitacao,
    UsuarioEnvolvido,
)
from app.modulos.solicitacao.infra.modelos import (
    AnexoSolicitacaoModelo,
    SolicitacaoHorarioModelo,
    SolicitacaoModelo,
)
from app.modulos.usuarios.infra.modelos import UsuarioModelo


class SolicitacaoRepositorio(SolicitacaoRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, id_solicitacao: int) -> Solicitacao | None:
        modelo = (
            self.db.query(SolicitacaoModelo)
            .options(
                joinedload(SolicitacaoModelo.usuarios_envolvidos),
                joinedload(SolicitacaoModelo.horarios),
                joinedload(SolicitacaoModelo.anexos),
            )
            .filter(SolicitacaoModelo.id == id_solicitacao)
            .first()
        )
        return self._converter(modelo) if modelo else None

    def buscar_todas(self) -> list[Solicitacao]:
        modelos = (
            self.db.query(SolicitacaoModelo)
            .options(
                joinedload(SolicitacaoModelo.usuarios_envolvidos),
                joinedload(SolicitacaoModelo.horarios),
                joinedload(SolicitacaoModelo.anexos),
            )
            .all()
        )
        return [self._converter(modelo) for modelo in modelos]

    def buscar_por_solicitante(self, id_solicitante: int) -> list[Solicitacao]:
        modelos = (
            self.db.query(SolicitacaoModelo)
            .options(
                joinedload(SolicitacaoModelo.usuarios_envolvidos),
                joinedload(SolicitacaoModelo.horarios),
                joinedload(SolicitacaoModelo.anexos),
            )
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
            horarios=[
                SolicitacaoHorarioModelo(
                    data_reserva=horario.data_reserva,
                    hora_inicio=horario.hora_inicio,
                    hora_fim=horario.hora_fim,
                )
                for horario in solicitacao.horarios
            ],
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        solicitacao_salva = self.buscar_por_id(modelo.id)
        if solicitacao_salva is None:
            raise EntidadeNaoEncontradaErro("Solicitação", modelo.id)
        return solicitacao_salva

    def decidir(
        self,
        id_solicitacao: int,
        status: StatusSolicitacao,
        justificativa: str,
    ) -> Solicitacao:
        try:
            modelo = (
                self.db.query(SolicitacaoModelo)
                .options(joinedload(SolicitacaoModelo.horarios))
                .filter(SolicitacaoModelo.id == id_solicitacao)
                .with_for_update()
                .first()
            )
            if modelo is None:
                raise EntidadeNaoEncontradaErro(
                    "Solicitação", id_solicitacao
                )
            if modelo.status != StatusSolicitacao.PENDENTE.value:
                raise ConflitoDeDadosErro(
                    "Somente solicitações pendentes podem receber decisão."
                )
            modelo.status = status.value
            modelo.decisao_justificativa = justificativa
            self.db.commit()
            solicitacao_decidida = self.buscar_por_id(id_solicitacao)
            if solicitacao_decidida is None:
                raise EntidadeNaoEncontradaErro(
                    "Solicitação", id_solicitacao
                )
            return solicitacao_decidida
        except Exception:
            self.db.rollback()
            raise

    def rollback(self) -> None:
        self.db.rollback()

    def buscar_anexo(
        self, id_solicitacao: int, id_anexo: int
    ) -> AnexoSolicitacao | None:
        modelo = (
            self.db.query(AnexoSolicitacaoModelo)
            .filter(
                AnexoSolicitacaoModelo.id == id_anexo,
                AnexoSolicitacaoModelo.id_solicitacao == id_solicitacao,
            )
            .first()
        )
        return self._converter_anexo(modelo) if modelo else None

    def salvar_anexo(
        self,
        id_solicitacao: int,
        nome_arquivo: str,
        url_caminho: str,
        tipo_arquivo: str,
        data_upload: datetime,
    ) -> AnexoSolicitacao:
        modelo = AnexoSolicitacaoModelo(
            id_solicitacao=id_solicitacao,
            nome_arquivo=nome_arquivo,
            url_caminho=url_caminho,
            tipo_arquivo=tipo_arquivo,
            data_upload=data_upload,
        )
        self.db.add(modelo)
        try:
            self.db.commit()
        except SQLAlchemyError as erro:
            self.db.rollback()
            raise FalhaPersistenciaErro() from erro
        self.db.refresh(modelo)
        return self._converter_anexo(modelo)

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
            horarios=[
                HorarioSolicitacao(
                    id=horario.id,
                    data_reserva=horario.data_reserva,
                    hora_inicio=horario.hora_inicio,
                    hora_fim=horario.hora_fim,
                )
                for horario in modelo.horarios
            ],
            anexos=[
                SolicitacaoRepositorio._converter_anexo(anexo)
                for anexo in modelo.anexos
            ],
        )

    @staticmethod
    def _converter_anexo(modelo: AnexoSolicitacaoModelo) -> AnexoSolicitacao:
        return AnexoSolicitacao(
            id=modelo.id,
            nome_arquivo=modelo.nome_arquivo,
            url_caminho=modelo.url_caminho,
            tipo_arquivo=modelo.tipo_arquivo,
            data_upload=modelo.data_upload,
        )