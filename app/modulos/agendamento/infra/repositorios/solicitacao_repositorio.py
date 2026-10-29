from datetime import datetime
from datetime import date, time

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    ConflitoDeDadosErro,
    EntidadeNaoEncontradaErro,
    FalhaPersistenciaErro,
    RegraDeNegocioErro,
)
from app.modulos.agendamento.dominio.contratos import SolicitacaoRepositorioContrato
from app.modulos.agendamento.dominio.entidades import (
    AnexoSolicitacao,
    EspacoRelacionadoSolicitacao,
    HorarioSolicitacao,
    InteracaoSolicitacao,
    ProjetoRelacionadoSolicitacao,
    Solicitacao,
    SolicitanteSolicitacao,
    SituacaoInteracaoSolicitacao,
    StatusSolicitacao,
    TipoInteracaoSolicitacao,
    UsuarioEnvolvido,
)
from app.modulos.agendamento.infra.modelos import (
    AnexoSolicitacaoModelo,
    SolicitacaoInteracaoModelo,
    SolicitacaoHorarioModelo,
    SolicitacaoModelo,
)
from app.modulos.espacos.infra.modelos import RecursoModelo
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
                selectinload(SolicitacaoModelo.recursos),
                selectinload(SolicitacaoModelo.interacoes),
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
                selectinload(SolicitacaoModelo.recursos),
                selectinload(SolicitacaoModelo.interacoes),
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
                selectinload(SolicitacaoModelo.recursos),
                selectinload(SolicitacaoModelo.interacoes),
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
        recursos = (
            self.db.query(RecursoModelo)
            .filter(RecursoModelo.id.in_(solicitacao.ids_recursos))
            .all()
            if solicitacao.ids_recursos
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
            recursos=recursos,
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

    def solicitar_complementacao(
        self, id_solicitacao: int, id_usuario: int, mensagem: str
    ) -> Solicitacao:
        modelo = self._buscar_modelo_para_atualizar(id_solicitacao)
        if modelo.status != StatusSolicitacao.PENDENTE.value:
            raise ConflitoDeDadosErro(
                "Somente solicitações pendentes podem receber pedido de complementação."
            )
        modelo.status = StatusSolicitacao.AGUARDANDO_COMPLEMENTACAO.value
        modelo.interacoes.append(
            self._nova_interacao(
                id_usuario,
                TipoInteracaoSolicitacao.COMPLEMENTACAO_SOLICITADA,
                SituacaoInteracaoSolicitacao.AGUARDANDO_RESPOSTA,
                mensagem,
            )
        )
        return self._salvar_interacao(id_solicitacao)

    def responder_complementacao(
        self, id_solicitacao: int, id_usuario: int, mensagem: str
    ) -> Solicitacao:
        modelo = self._buscar_modelo_para_atualizar(id_solicitacao)
        if modelo.id_solicitante != id_usuario:
            raise AcessoNegadoErro(
                "Somente o solicitante pode responder à complementação."
            )
        if modelo.status != StatusSolicitacao.AGUARDANDO_COMPLEMENTACAO.value:
            raise ConflitoDeDadosErro(
                "A solicitação não está aguardando complementação."
            )
        interacao = next(
            (
                item
                for item in reversed(modelo.interacoes)
                if item.tipo
                == TipoInteracaoSolicitacao.COMPLEMENTACAO_SOLICITADA.value
                and item.situacao
                == SituacaoInteracaoSolicitacao.AGUARDANDO_RESPOSTA.value
            ),
            None,
        )
        if interacao is None:
            raise RegraDeNegocioErro(
                "Não existe pedido de complementação aguardando resposta."
            )
        interacao.situacao = SituacaoInteracaoSolicitacao.RESPONDIDA.value
        modelo.interacoes.append(
            self._nova_interacao(
                id_usuario,
                TipoInteracaoSolicitacao.COMPLEMENTACAO_RESPONDIDA,
                SituacaoInteracaoSolicitacao.RESPONDIDA,
                mensagem,
            )
        )
        modelo.status = StatusSolicitacao.PENDENTE.value
        return self._salvar_interacao(id_solicitacao)

    def propor_replanejamento(
        self,
        id_solicitacao: int,
        id_usuario: int,
        mensagem: str,
        horarios: list[HorarioSolicitacao],
        ids_recursos: list[int],
    ) -> Solicitacao:
        modelo = self._buscar_modelo_para_atualizar(id_solicitacao)
        if modelo.status != StatusSolicitacao.PENDENTE.value:
            raise ConflitoDeDadosErro(
                "Somente solicitações pendentes podem receber uma proposta."
            )
        dados = {
            "horarios": [
                {
                    "data_reserva": horario.data_reserva.isoformat(),
                    "hora_inicio": horario.hora_inicio.isoformat(),
                    "hora_fim": horario.hora_fim.isoformat(),
                }
                for horario in horarios
            ],
            "ids_recursos": ids_recursos,
        }
        modelo.status = StatusSolicitacao.AGUARDANDO_RESPOSTA_PROPOSTA.value
        modelo.interacoes.append(
            self._nova_interacao(
                id_usuario,
                TipoInteracaoSolicitacao.REPLANEJAMENTO_PROPOSTO,
                SituacaoInteracaoSolicitacao.AGUARDANDO_RESPOSTA,
                mensagem,
                dados,
            )
        )
        return self._salvar_interacao(id_solicitacao)

    def responder_proposta(
        self,
        id_solicitacao: int,
        id_interacao: int,
        id_usuario: int,
        aceita: bool,
        mensagem: str,
    ) -> Solicitacao:
        modelo = self._buscar_modelo_para_atualizar(id_solicitacao)
        if modelo.id_solicitante != id_usuario:
            raise AcessoNegadoErro(
                "Somente o solicitante pode responder à proposta."
            )
        if modelo.status != StatusSolicitacao.AGUARDANDO_RESPOSTA_PROPOSTA.value:
            raise ConflitoDeDadosErro(
                "A solicitação não está aguardando resposta de proposta."
            )
        proposta = next(
            (
                item
                for item in modelo.interacoes
                if item.id == id_interacao
                and item.tipo
                == TipoInteracaoSolicitacao.REPLANEJAMENTO_PROPOSTO.value
                and item.situacao
                == SituacaoInteracaoSolicitacao.AGUARDANDO_RESPOSTA.value
            ),
            None,
        )
        if proposta is None:
            raise EntidadeNaoEncontradaErro("Proposta pendente", id_interacao)

        situacao_resposta = (
            SituacaoInteracaoSolicitacao.ACEITA
            if aceita
            else SituacaoInteracaoSolicitacao.RECUSADA
        )
        proposta.situacao = situacao_resposta.value
        modelo.interacoes.append(
            self._nova_interacao(
                id_usuario,
                TipoInteracaoSolicitacao.PROPOSTA_RESPONDIDA,
                situacao_resposta,
                mensagem,
                {"id_interacao_proposta": id_interacao},
            )
        )
        modelo.status = StatusSolicitacao.PENDENTE.value
        if aceita:
            dados = proposta.dados or {}
            horarios = dados.get("horarios", [])
            ids_recursos = dados.get("ids_recursos", [])
            modelo.horarios = [
                SolicitacaoHorarioModelo(
                    data_reserva=date.fromisoformat(horario["data_reserva"]),
                    hora_inicio=time.fromisoformat(horario["hora_inicio"]),
                    hora_fim=time.fromisoformat(horario["hora_fim"]),
                )
                for horario in horarios
            ]
            modelo.recursos = (
                self.db.query(RecursoModelo)
                .filter(RecursoModelo.id.in_(ids_recursos))
                .all()
                if ids_recursos
                else []
            )
            self.db.flush()
            solicitacao = self.buscar_por_id(id_solicitacao)
            if solicitacao is None:
                raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)
            return solicitacao
        return self._salvar_interacao(id_solicitacao)

    def _buscar_modelo_para_atualizar(self, id_solicitacao: int) -> SolicitacaoModelo:
        modelo = (
            self.db.query(SolicitacaoModelo)
            .options(
                selectinload(SolicitacaoModelo.interacoes),
                selectinload(SolicitacaoModelo.horarios),
                selectinload(SolicitacaoModelo.recursos),
            )
            .filter(SolicitacaoModelo.id == id_solicitacao)
            .with_for_update()
            .first()
        )
        if modelo is None:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)
        return modelo

    @staticmethod
    def _nova_interacao(
        id_usuario: int,
        tipo: TipoInteracaoSolicitacao,
        situacao: SituacaoInteracaoSolicitacao,
        mensagem: str,
        dados: dict[str, object] | None = None,
    ) -> SolicitacaoInteracaoModelo:
        return SolicitacaoInteracaoModelo(
            id_usuario=id_usuario,
            tipo=tipo.value,
            situacao=situacao.value,
            mensagem=mensagem,
            dados=dados,
        )

    def _salvar_interacao(self, id_solicitacao: int) -> Solicitacao:
        try:
            self.db.commit()
        except SQLAlchemyError as erro:
            self.db.rollback()
            raise FalhaPersistenciaErro() from erro
        solicitacao = self.buscar_por_id(id_solicitacao)
        if solicitacao is None:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)
        return solicitacao

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
            ids_recursos=[recurso.id for recurso in modelo.recursos],
            anexos=[
                SolicitacaoRepositorio._converter_anexo(anexo)
                for anexo in modelo.anexos
            ],
            interacoes=[
                InteracaoSolicitacao(
                    id=interacao.id,
                    tipo=TipoInteracaoSolicitacao(interacao.tipo),
                    situacao=SituacaoInteracaoSolicitacao(interacao.situacao),
                    mensagem=interacao.mensagem,
                    dados=interacao.dados,
                    id_usuario=interacao.id_usuario,
                    data_criacao=interacao.data_criacao,
                )
                for interacao in modelo.interacoes
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
