from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.compartilhado.infra.config import Config
from app.compartilhado.infra.seeds import popular_dados
from app.modulos.agendamento.infra.modelos import (
    ReservaAgendaModelo,
    SolicitacaoModelo,
)
from app.modulos.espacos.infra.modelos import (
    EspacoHorarioFuncionamentoModelo,
    EspacoModelo,
    RecursoModelo,
)
from app.modulos.projetos.infra.modelos import ProjetoModelo
from app.modulos.usuarios.infra.modelos import UsuarioModelo


def test_config_carrega_senha_seed_do_arquivo_env(tmp_path) -> None:
    arquivo_env = tmp_path / ".env"
    arquivo_env.write_text(
        "URL_BANCO_DADOS=sqlite://\n"
        "CHAVE_SECRETA=chave-de-teste\n"
        "SEED_PASSWORD=SenhaDeTeste123!\n",
        encoding="utf-8",
    )

    configuracao = Config(_env_file=arquivo_env)

    assert configuracao.seed_password is not None
    assert configuracao.seed_password.get_secret_value() == "SenhaDeTeste123!"


def test_popular_dados_e_idempotente(
    test_session_factory: sessionmaker[Session],
) -> None:
    with test_session_factory() as db:
        popular_dados(db, "SenhaDeTeste123!")
        db.commit()

        popular_dados(db, "SenhaDeTeste123!")
        db.commit()

        assert db.scalar(select(func.count()).select_from(UsuarioModelo)) == 5
        assert db.scalar(select(func.count()).select_from(EspacoModelo)) == 2
        assert db.scalar(select(func.count()).select_from(RecursoModelo)) == 2
        assert (
            db.scalar(
                select(func.count()).select_from(EspacoHorarioFuncionamentoModelo)
            )
            == 10
        )
        assert db.scalar(select(func.count()).select_from(ProjetoModelo)) == 1
        assert db.scalar(select(func.count()).select_from(SolicitacaoModelo)) == 2
        assert db.scalar(select(func.count()).select_from(ReservaAgendaModelo)) == 1
