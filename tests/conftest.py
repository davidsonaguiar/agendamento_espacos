from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.compartilhado.infra.banco_dados import Base, pegar_banco_dados
from app.compartilhado.infra.seguranca.codificador_senha import CodificadorSenha
from app.modulos.agendamento.casos_uso.anexar_arquivo import (
    AnexarArquivoSolicitacaoCasoDeUso,
)
from app.modulos.agendamento.casos_uso.obter_url_anexo import (
    ObterUrlAnexoCasoDeUso,
)
from app.modulos.agendamento.infra.repositorios import SolicitacaoRepositorio
from app.modulos.agendamento.interface.dependencias import (
    pegar_caso_de_uso_anexar_arquivo,
    pegar_caso_de_uso_obter_url_anexo,
)
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.usuarios.infra.modelos import UsuarioModelo
from main import app


class FakeArmazenamento:
    def __init__(self) -> None:
        self.arquivos: dict[str, bytes] = {}

    def enviar(self, caminho: str, conteudo: bytes, tipo_conteudo: str) -> None:
        self.arquivos[caminho] = conteudo

    def remover(self, caminho: str) -> None:
        self.arquivos.pop(caminho, None)

    def criar_url_assinada(self, caminho: str, validade_segundos: int) -> str:
        return f"https://storage.test/{caminho}?expires={validade_segundos}"


@pytest.fixture
def test_session_factory() -> Generator[sessionmaker[Session], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def fake_storage() -> FakeArmazenamento:
    return FakeArmazenamento()


@pytest.fixture
def client(
    test_session_factory: sessionmaker[Session],
    fake_storage: FakeArmazenamento,
) -> Generator[TestClient, None, None]:
    @asynccontextmanager
    async def no_lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield

    original_lifespan = app.router.lifespan_context

    def override_database() -> Generator[Session, None, None]:
        with test_session_factory() as db:
            yield db

    def override_anexar_arquivo(
        db: Session = Depends(pegar_banco_dados),
    ) -> AnexarArquivoSolicitacaoCasoDeUso:
        return AnexarArquivoSolicitacaoCasoDeUso(
            SolicitacaoRepositorio(db),
            fake_storage,
        )

    def override_obter_url_anexo(
        db: Session = Depends(pegar_banco_dados),
    ) -> ObterUrlAnexoCasoDeUso:
        return ObterUrlAnexoCasoDeUso(
            SolicitacaoRepositorio(db),
            fake_storage,
        )

    app.router.lifespan_context = no_lifespan
    app.dependency_overrides[pegar_banco_dados] = override_database
    app.dependency_overrides[pegar_caso_de_uso_anexar_arquivo] = (
        override_anexar_arquivo
    )
    app.dependency_overrides[pegar_caso_de_uso_obter_url_anexo] = (
        override_obter_url_anexo
    )

    try:
        with TestClient(app, base_url="http://localhost") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.router.lifespan_context = original_lifespan


@pytest.fixture
def usuarios(
    test_session_factory: sessionmaker[Session],
) -> dict[PerfilUsuario, int]:
    senha_codificada = CodificadorSenha().codificar_senha("SenhaValida123!")
    perfis = list(PerfilUsuario)
    with test_session_factory() as db:
        registros = [
            UsuarioModelo(
                nome_completo=f"Usuário {perfil.value}",
                cpf=f"{index:011d}",
                vinculo_institucional=f"MAT{index:05d}",
                email=f"{perfil.name.lower()}@example.com",
                senha_codificada=senha_codificada,
                perfil=perfil,
                ativo=True,
            )
            for index, perfil in enumerate(perfis, start=1)
        ]
        db.add_all(registros)
        db.commit()
        return {
            registro.perfil: registro.id
            for registro in registros
        }


def cabecalhos_autenticacao(id_usuario: int) -> dict[str, str]:
    from app.compartilhado.infra.seguranca.jwt import JWT

    token = JWT().criar_token_acesso(id_usuario)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers(usuarios: dict[PerfilUsuario, int]):
    return {
        perfil: cabecalhos_autenticacao(id_usuario)
        for perfil, id_usuario in usuarios.items()
    }
