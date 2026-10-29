from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.usuarios.infra.modelos import UsuarioModelo


def test_administrador_lista_usuarios(client, headers):
    resposta = client.get(
        "/usuarios/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == len(PerfilUsuario)


def test_coordenador_lista_usuarios(client, headers):
    resposta = client.get(
        "/usuarios/?perfil=Monitor&skip=0&limit=10",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 200
    assert all(
        usuario["perfil"] == PerfilUsuario.MONITOR.value
        for usuario in resposta.json()
    )


def test_listar_usuarios_aplica_filtros_de_perfil_e_status(
    client, headers, test_session_factory, usuarios
):
    with test_session_factory() as db:
        servidor = (
            db.query(UsuarioModelo)
            .filter(UsuarioModelo.id == usuarios[PerfilUsuario.SERVIDOR])
            .one()
        )
        servidor.ativo = False
        db.commit()

    resposta = client.get(
        "/usuarios/?perfil=Servidor&ativo=false",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["perfil"] == PerfilUsuario.SERVIDOR.value
    assert resposta.json()[0]["ativo"] is False


def test_listar_usuarios_aplica_paginacao(client, headers):
    resposta = client.get(
        "/usuarios/?skip=1&limit=2",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_listar_usuarios_rejeita_perfil_sem_permissao(client, headers):
    resposta = client.get(
        "/usuarios/",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 403


def test_listar_usuarios_rejeita_requisicao_sem_token(client):
    resposta = client.get("/usuarios/")

    assert resposta.status_code == 401


def test_listar_usuarios_rejeita_parametros_de_paginacao_invalidos(
    client, headers
):
    resposta_skip = client.get(
        "/usuarios/?skip=-1",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )
    resposta_limit = client.get(
        "/usuarios/?limit=101",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta_skip.status_code == 422
    assert resposta_limit.status_code == 422


def test_listar_usuarios_rejeita_perfil_desconhecido(client, headers):
    resposta = client.get(
        "/usuarios/?perfil=Desconhecido",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 422
