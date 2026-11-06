from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.compartilhado.infra.banco_dados import Base, SessaoLocal, motor
from app.compartilhado.infra.config import config
from app.compartilhado.infra.seguranca.codificador_senha import CodificadorSenha
from app.modulos.agendamento.infra.modelos import (
    ReservaAgendaModelo,
    SolicitacaoHorarioModelo,
    SolicitacaoModelo,
)
from app.modulos.espacos.infra.modelos import (
    EspacoHorarioFuncionamentoModelo,
    EspacoModelo,
    RecursoModelo,
)
from app.modulos.projetos.infra.modelos import (
    ProjetoModelo,
    ProjetoParticipanteModelo,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.usuarios.infra.modelos import UsuarioModelo

def _criar_usuarios(db: Session, senha: str) -> dict[str, UsuarioModelo]:
    perfis = {
        "administrador": PerfilUsuario.ADMINISTRADOR,
        "coordenador": PerfilUsuario.COORDENADOR,
        "servidor": PerfilUsuario.SERVIDOR,
        "monitor": PerfilUsuario.MONITOR,
        "aluno": PerfilUsuario.ALUNO,
    }
    codificador = CodificadorSenha()
    senha_codificada: str | None = None
    usuarios: dict[str, UsuarioModelo] = {}

    for indice, (chave, perfil) in enumerate(perfis.items(), start=1):
        email = f"seed.{chave}@example.com"
        usuario = db.scalar(
            select(UsuarioModelo).where(UsuarioModelo.email == email)
        )
        if usuario is None:
            if senha_codificada is None:
                senha_codificada = codificador.codificar_senha(senha)
            usuario = UsuarioModelo(
                nome_completo=f"Usuário de demonstração - {perfil.value}",
                cpf=f"000.000.000-{indice:02d}",
                vinculo_institucional=f"SEED-{indice:05d}",
                email=email,
                senha_codificada=senha_codificada,
                perfil=perfil,
                ativo=True,
            )
            db.add(usuario)
        usuarios[chave] = usuario

    db.flush()
    return usuarios


def _criar_espacos(
    db: Session,
    usuarios: dict[str, UsuarioModelo],
) -> tuple[EspacoModelo, RecursoModelo, EspacoModelo, RecursoModelo]:
    definicoes = (
        (
            "Sala multiuso (seed)",
            "Espaço de demonstração para atividades e eventos.",
            30,
            "Bloco A",
            "Projetor (seed)",
            "Audiovisual",
        ),
        (
            "Sala de reuniões (seed)",
            "Espaço de demonstração para reuniões de projeto.",
            12,
            "Bloco A",
            "Kit de videoconferência (seed)",
            "Videoconferência",
        ),
    )
    resultados: list[tuple[EspacoModelo, RecursoModelo]] = []

    for nome, descricao, capacidade, bloco, nome_recurso, tipo_recurso in definicoes:
        espaco = db.scalar(select(EspacoModelo).where(EspacoModelo.nome == nome))
        if espaco is None:
            espaco = EspacoModelo(
                nome=nome,
                descricao=descricao,
                capacidade=capacidade,
                bloco=bloco,
                disponibilidade=True,
            )
            db.add(espaco)
            db.flush()

        for dia_semana in range(5):
            horario = db.scalar(
                select(EspacoHorarioFuncionamentoModelo).where(
                    EspacoHorarioFuncionamentoModelo.id_espaco == espaco.id,
                    EspacoHorarioFuncionamentoModelo.dia_semana == dia_semana,
                )
            )
            if horario is None:
                db.add(
                    EspacoHorarioFuncionamentoModelo(
                        id_espaco=espaco.id,
                        dia_semana=dia_semana,
                        hora_abertura=time(8),
                        hora_fechamento=time(18),
                        ativo=True,
                    )
                )

        for chave_usuario in ("administrador", "coordenador"):
            usuario = usuarios[chave_usuario]
            if usuario not in espaco.usuarios_vinculados:
                espaco.usuarios_vinculados.append(usuario)

        recurso = db.scalar(
            select(RecursoModelo).where(
                RecursoModelo.id_espaco == espaco.id,
                RecursoModelo.nome == nome_recurso,
            )
        )
        if recurso is None:
            recurso = RecursoModelo(
                nome=nome_recurso,
                tipo=tipo_recurso,
                autorizacao_necessaria=False,
                disponibilidade=True,
                reserva_independente=False,
                id_espaco=espaco.id,
            )
            db.add(recurso)
        resultados.append((espaco, recurso))

    db.flush()
    return resultados[0][0], resultados[0][1], resultados[1][0], resultados[1][1]


def _criar_projeto(
    db: Session,
    usuarios: dict[str, UsuarioModelo],
) -> ProjetoModelo:
    descricao = "Projeto de demonstração (seed)"
    projeto = db.scalar(
        select(ProjetoModelo).where(
            ProjetoModelo.descricao == descricao,
            ProjetoModelo.id_responsavel == usuarios["coordenador"].id,
        )
    )
    if projeto is None:
        projeto = ProjetoModelo(
            descricao=descricao,
            finalidade="Dados de demonstração para validar o fluxo de agendamento.",
            id_responsavel=usuarios["coordenador"].id,
            id_criador=usuarios["administrador"].id,
            quantidade_participantes=2,
            participantes=[
                ProjetoParticipanteModelo(
                    usuario=usuarios["aluno"],
                    papel_no_projeto="Pesquisador",
                ),
                ProjetoParticipanteModelo(
                    usuario=usuarios["monitor"],
                    papel_no_projeto="Apoio técnico",
                ),
            ],
        )
        db.add(projeto)
        db.flush()
    return projeto


def _proxima_data_util(dias: int) -> date:
    data_reserva = date.today() + timedelta(days=dias)
    while data_reserva.weekday() >= 5:
        data_reserva += timedelta(days=1)
    return data_reserva


def _criar_solicitacao(
    db: Session,
    *,
    finalidade: str,
    status: str,
    espaco: EspacoModelo,
    recurso: RecursoModelo,
    projeto: ProjetoModelo,
    solicitante: UsuarioModelo,
    data_reserva: date,
) -> SolicitacaoModelo:
    solicitacao = db.scalar(
        select(SolicitacaoModelo).where(
            SolicitacaoModelo.finalidade == finalidade,
            SolicitacaoModelo.id_solicitante == solicitante.id,
            SolicitacaoModelo.id_projeto == projeto.id,
        )
    )
    if solicitacao is None:
        solicitacao = SolicitacaoModelo(
            finalidade=finalidade,
            status=status,
            id_projeto=projeto.id,
            id_solicitante=solicitante.id,
            id_espaco=espaco.id,
            espaco_reservado=True,
        )
        db.add(solicitacao)
        db.flush()
    if solicitante not in solicitacao.usuarios_envolvidos:
        solicitacao.usuarios_envolvidos.append(solicitante)
    if recurso not in solicitacao.recursos:
        solicitacao.recursos.append(recurso)
    if not solicitacao.horarios:
        solicitacao.horarios.append(
            SolicitacaoHorarioModelo(
                data_reserva=data_reserva,
                hora_inicio=time(10),
                hora_fim=time(11),
            )
        )
    return solicitacao


def popular_dados(db: Session, senha: str) -> None:
    usuarios = _criar_usuarios(db, senha)
    sala_multiuso, projetor, sala_reunioes, videoconferencia = _criar_espacos(
        db,
        usuarios,
    )
    projeto = _criar_projeto(db, usuarios)

    _criar_solicitacao(
        db,
        finalidade="Reunião de planejamento (seed)",
        status="Pendente",
        espaco=sala_multiuso,
        recurso=projetor,
        projeto=projeto,
        solicitante=usuarios["aluno"],
        data_reserva=_proxima_data_util(7),
    )
    solicitacao_aprovada = _criar_solicitacao(
        db,
        finalidade="Apresentação do projeto (seed)",
        status="Aprovado",
        espaco=sala_reunioes,
        recurso=videoconferencia,
        projeto=projeto,
        solicitante=usuarios["monitor"],
        data_reserva=_proxima_data_util(14),
    )
    if db.scalar(
        select(ReservaAgendaModelo).where(
            ReservaAgendaModelo.id_solicitacao == solicitacao_aprovada.id
        )
    ) is None:
        horario = solicitacao_aprovada.horarios[0]
        db.add(
            ReservaAgendaModelo(
                id_solicitacao=solicitacao_aprovada.id,
                id_espaco=sala_reunioes.id,
                data_hora_inicio=datetime.combine(
                    horario.data_reserva,
                    horario.hora_inicio,
                ),
                data_hora_fim=datetime.combine(
                    horario.data_reserva,
                    horario.hora_fim,
                ),
                situacao="Confirmada",
                espaco_reservado=True,
                recursos=[videoconferencia],
            )
        )


def main() -> None:
    if config.seed_password is None or not config.seed_password.get_secret_value():
        raise SystemExit(
            "Defina SEED_PASSWORD no ambiente ou no arquivo .env antes de executar."
        )
    senha = config.seed_password.get_secret_value()

    Base.metadata.create_all(bind=motor)
    with SessaoLocal.begin() as db:
        popular_dados(db, senha)

    print("Seeds criadas ou já existentes.")


if __name__ == "__main__":
    main()
