from sqlalchemy import Engine, inspect, text

from app.modulos.usuarios.infra.modelos import UsuarioModelo


def migrar_papeis_usuarios(engine: Engine) -> None:
    if engine.dialect.name == "postgresql":
        tipo_perfil = UsuarioModelo.__table__.c.perfil.type
        nome_tipo = engine.dialect.identifier_preparer.quote(tipo_perfil.name)
        with engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conexao:
            conexao.exec_driver_sql(
                f"ALTER TYPE {nome_tipo} ADD VALUE IF NOT EXISTS 'MEMBRO'"
            )

    with engine.begin() as conexao:
        tabelas = set(inspect(conexao).get_table_names())
        if "espaco_usuario" in tabelas:
            colunas = {
                coluna["name"]
                for coluna in inspect(conexao).get_columns("espaco_usuario")
            }
            if "perfil_espaco" not in colunas:
                conexao.exec_driver_sql(
                    "ALTER TABLE espaco_usuario "
                    "ADD COLUMN perfil_espaco VARCHAR(20)"
                )
                vinculos = conexao.execute(
                    text(
                        "SELECT espaco_usuario.id_espaco, "
                        "espaco_usuario.id_usuario, usuario.perfil "
                        "FROM espaco_usuario "
                        "JOIN usuario ON usuario.id = espaco_usuario.id_usuario"
                    )
                ).mappings()
                papeis_legados = {
                    "COORDENADOR": "Coordenador",
                    "MONITOR": "Monitor",
                    "Coordenador": "Coordenador",
                    "Monitor": "Monitor",
                }
                for vinculo in vinculos:
                    conexao.execute(
                        text(
                            "UPDATE espaco_usuario SET perfil_espaco = :perfil "
                            "WHERE id_espaco = :id_espaco "
                            "AND id_usuario = :id_usuario"
                        ),
                        {
                            "perfil": papeis_legados.get(vinculo["perfil"]),
                            "id_espaco": vinculo["id_espaco"],
                            "id_usuario": vinculo["id_usuario"],
                        },
                    )

        if "usuario" in tabelas:
            conexao.execute(
                text(
                    "UPDATE usuario SET perfil = 'MEMBRO' "
                    "WHERE CAST(perfil AS TEXT) IN "
                    "('COORDENADOR', 'SERVIDOR', 'MONITOR', 'ALUNO')"
                )
            )
