from datetime import datetime

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.compartilhado.dominio.erros import (
    EntidadeNaoEncontradaErro,
    FalhaPersistenciaErro,
)
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import (
    AnexoSolicitacao,
    EspacoRelacionadoSolicitacao,
    HorarioSolicitacao,
    ProjetoRelacionadoSolicitacao,
    Solicitacao,
    SolicitanteSolicitacao,
    StatusSolicitacao,
    UsuarioEnvolvido,
)
from app.modulos.agendamento.infra.modelos import (
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
                joinedload(SolicitacaoModelo.projeto),
                joinedload(SolicitacaoModelo.espaco),
                joinedload(SolicitacaoModelo.solicitante),
                selectinload(SolicitacaoModelo.usuarios_envolvidos),
                selectinload(SolicitacaoModelo.horarios),
                selectinload(SolicitacaoModelo.anexos),
            )
            .filter(SolicitacaoModelo.id == id_solicitacao)
            .first()
        )
        return self._converter(modelo) if modelo else None

    def buscar_todas(self) -> list[Solicitacao]:
        modelos = (
            self.db.query(SolicitacaoModelo)
            .options(
                joinedload(SolicitacaoModelo.projeto),
                joinedload(SolicitacaoModelo.espaco),
                joinedload(SolicitacaoModelo.solicitante),
                selectinload(SolicitacaoModelo.usuarios_envolvidos),
                selectinload(SolicitacaoModelo.horarios),
                selectinload(SolicitacaoModelo.anexos),
            )
            .all()
        )
        return [self._converter(modelo) for modelo in modelos]

    def buscar_por_solicitante(self, id_solicitante: int) -> list[Solicitacao]:
        modelos = (
            self.db.query(SolicitacaoModelo)
            .options(
                joinedload(SolicitacaoModelo.projeto),
                joinedload(SolicitacaoModelo.espaco),
                joinedload(SolicitacaoModelo.solicitante),
                selectinload(SolicitacaoModelo.usuarios_envolvidos),
                selectinload(SolicitacaoModelo.horarios),
                selectinload(SolicitacaoModelo.anexos),
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

    def cancelar(self, id_solicitacao: int) -> Solicitacao | None:
        resultado = self.db.execute(
            update(SolicitacaoModelo)
            .where(
                SolicitacaoModelo.id == id_solicitacao,
                SolicitacaoModelo.status == StatusSolicitacao.PENDENTE.value,
            )
            .values(status=StatusSolicitacao.CANCELADA.value)
        )
        if resultado.rowcount != 1:
            self.db.rollback()
            return None

        self.db.commit()
        return self.buscar_por_id(id_solicitacao)

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
            projeto=(
                ProjetoRelacionadoSolicitacao(
                    id=modelo.projeto.id,
                    descricao=modelo.projeto.descricao,
                    finalidade=modelo.projeto.finalidade,
                )
                if modelo.projeto
                else None
            ),
            espaco=(
                EspacoRelacionadoSolicitacao(
                    id=modelo.espaco.id,
                    nome=modelo.espaco.nome,
                    descricao=modelo.espaco.descricao,
                    capacidade=modelo.espaco.capacidade,
                    bloco=modelo.espaco.bloco,
                    disponibilidade=modelo.espaco.disponibilidade,
                )
                if modelo.espaco
                else None
            ),
            solicitante=SolicitanteSolicitacao(
                id=modelo.solicitante.id,
                nome_completo=modelo.solicitante.nome_completo,
                perfil=modelo.solicitante.perfil.value,
            ),
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