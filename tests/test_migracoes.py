import asyncio

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy import inspect as inspecionar

import app.compartilhado.infra.ciclo_vida as ciclo_vida

from app.compartilhado.infra.migracoes import migrar_papeis_usuarios


def test_migrar_papeis_globais_preserva_perfis_locais_existentes():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as conexao:
            conexao.exec_driver_sql(
                "CREATE TABLE usuario (id INTEGER PRIMARY KEY, perfil VARCHAR(30))"
            )
            conexao.exec_driver_sql(
                "CREATE TABLE espaco_usuario ("
                "id_espaco INTEGER, id_usuario INTEGER, "
                "PRIMARY KEY (id_espaco, id_usuario))"
            )
            conexao.execute(
                text("INSERT INTO usuario (id, perfil) VALUES (1, 'COORDENADOR')")
            )
            conexao.execute(
                text("INSERT INTO usuario (id, perfil) VALUES (2, 'MONITOR')")
            )
            conexao.execute(
                text("INSERT INTO usuario (id, perfil) VALUES (3, 'SERVIDOR')")
            )
            conexao.execute(
                text("INSERT INTO usuario (id, perfil) VALUES (4, 'ADMINISTRADOR')")
            )
            conexao.exec_driver_sql(
                "INSERT INTO espaco_usuario (id_espaco, id_usuario) VALUES "
                "(10, 1), (10, 2), (10, 4)"
            )

        migrar_papeis_usuarios(engine)

        with engine.connect() as conexao:
            perfis_usuarios = dict(
                conexao.execute(
                    text("SELECT id, perfil FROM usuario")
                ).all()
            )
            perfis_espaco = dict(
                conexao.execute(
                    text(
                        "SELECT id_usuario, perfil_espaco FROM espaco_usuario"
                    )
                ).all()
            )

        assert perfis_usuarios == {
            1: "MEMBRO",
            2: "MEMBRO",
            3: "MEMBRO",
            4: "ADMINISTRADOR",
        }
        assert perfis_espaco == {
            1: "Coordenador",
            2: "Monitor",
            4: None,
        }
    finally:
        engine.dispose()


def test_ciclo_de_vida_cria_tabelas_de_autenticacao(monkeypatch):
    engine = create_engine("sqlite://")
    monkeypatch.setattr(ciclo_vida, "motor", engine)

    async def iniciar_aplicacao():
        async with ciclo_vida.ciclo_de_vida_app(FastAPI()):
            pass

    try:
        asyncio.run(iniciar_aplicacao())
        tabelas = set(inspecionar(engine).get_table_names())
        assert {"sessao_autenticacao", "refresh_token"} <= tabelas
    finally:
        engine.dispose()
