from http.cookies import SimpleCookie

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.usuarios.infra.modelos import UsuarioModelo


def _refresh_cookie(resposta) -> str:
    cookie = SimpleCookie()
    cookie.load(resposta.headers["set-cookie"])
    return cookie["refresh_token"].value


def _login(client) -> tuple[dict, str]:
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "membro@example.com",
            "senha": "SenhaValida123!",
        },
    )
    assert resposta.status_code == 200, resposta.text
    return resposta.json(), _refresh_cookie(resposta)


def _cookie_header(token: str) -> dict[str, str]:
    return {"Cookie": f"refresh_token={token}"}


def test_login_emite_cookie_refresh_http_only(client, usuarios):
    resposta = client.post(
        "/usuarios/login",
        json={
            "identificacao": "membro@example.com",
            "senha": "SenhaValida123!",
        },
    )

    cabecalho_cookie = resposta.headers["set-cookie"].lower()
    assert resposta.status_code == 200
    assert "refresh_token=" in cabecalho_cookie
    assert "httponly" in cabecalho_cookie
    assert "secure" in cabecalho_cookie
    assert "samesite=lax" in cabecalho_cookie
    corpo = resposta.json()
    assert corpo["access_token"]
    assert corpo["token_type"] == "bearer"
    assert "refresh_token" not in corpo


def test_openapi_documenta_cookie_refresh_nas_respostas_e_endpoints(client):
    schema = client.get("/openapi.json").json()
    operacoes = schema["paths"]["/usuarios/login"]["post"], schema["paths"][
        "/usuarios/refresh"
    ]["post"]

    for operacao in operacoes:
        cookie_header = operacao["responses"]["200"]["headers"]["Set-Cookie"]
        assert "refresh_token" in cookie_header["description"]

    refresh = operacoes[1]
    cookie = next(
        parametro
        for parametro in refresh["parameters"]
        if parametro["in"] == "cookie" and parametro["name"] == "refresh_token"
    )
    assert "HttpOnly" in cookie["description"]


def test_refresh_rotaciona_e_reutilizacao_revoga_sessao(
    client,
    usuarios,
):
    login, refresh_original = _login(client)
    resposta_refresh = client.post(
        "/usuarios/refresh",
        headers=_cookie_header(refresh_original),
    )

    assert resposta_refresh.status_code == 200, resposta_refresh.text
    refresh_novo = _refresh_cookie(resposta_refresh)
    assert refresh_novo != refresh_original
    assert resposta_refresh.json()["access_token"] != login["access_token"]

    resposta_reutilizacao = client.post(
        "/usuarios/refresh",
        headers=_cookie_header(refresh_original),
    )
    assert resposta_reutilizacao.status_code == 401
    assert (
        client.get(
            "/usuarios/me",
            headers={"Authorization": f"Bearer {resposta_refresh.json()['access_token']}"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/refresh",
            headers=_cookie_header(refresh_novo),
        ).status_code
        == 401
    )
    assert login["access_token"]


def test_logout_invalida_sessao_atual(client, usuarios):
    login, refresh_token = _login(client)
    resposta = client.post(
        "/usuarios/logout",
        headers=_cookie_header(refresh_token),
    )

    assert resposta.status_code == 204
    assert (
        client.get(
            "/usuarios/me",
            headers={"Authorization": f"Bearer {login['access_token']}"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/refresh",
            headers=_cookie_header(refresh_token),
        ).status_code
        == 401
    )


def test_logout_todos_invalida_todas_as_sessoes(
    client,
    usuarios,
    headers,
):
    primeira_sessao, _ = _login(client)
    segunda_sessao, _ = _login(client)

    resposta = client.post(
        "/usuarios/logout-todos",
        headers=headers[PerfilUsuario.MEMBRO],
    )

    assert resposta.status_code == 204
    for sessao in (primeira_sessao, segunda_sessao):
        assert (
            client.get(
                "/usuarios/me",
                headers={"Authorization": f"Bearer {sessao['access_token']}"},
            ).status_code
            == 401
        )
    assert (
        client.get(
            "/usuarios/me",
            headers=headers[PerfilUsuario.MEMBRO],
        ).status_code
        == 401
    )


def test_troca_de_senha_invalida_sessoes_e_atualiza_credencial(
    client,
    usuarios,
):
    primeira_sessao, refresh_token = _login(client)
    segunda_sessao, _ = _login(client)
    resposta = client.post(
        "/usuarios/me/senha",
        headers={"Authorization": f"Bearer {primeira_sessao['access_token']}"},
        json={
            "senha_atual": "SenhaValida123!",
            "nova_senha": "SenhaNova123!",
        },
    )

    assert resposta.status_code == 204
    for sessao in (primeira_sessao, segunda_sessao):
        assert (
            client.get(
                "/usuarios/me",
                headers={"Authorization": f"Bearer {sessao['access_token']}"},
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/usuarios/refresh",
            headers=_cookie_header(refresh_token),
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/login",
            json={
                "identificacao": "membro@example.com",
                "senha": "SenhaValida123!",
            },
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/login",
            json={
                "identificacao": "membro@example.com",
                "senha": "SenhaNova123!",
            },
        ).status_code
        == 200
    )


def test_desativacao_de_usuario_revoga_sessoes(
    client,
    usuarios,
    test_session_factory,
):
    login, refresh_token = _login(client)
    with test_session_factory() as db:
        usuario = db.get(UsuarioModelo, usuarios[PerfilUsuario.MEMBRO])
        assert usuario is not None
        usuario.ativo = False
        db.commit()

    assert (
        client.get(
            "/usuarios/me",
            headers={"Authorization": f"Bearer {login['access_token']}"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/refresh",
            headers=_cookie_header(refresh_token),
        ).status_code
        == 401
    )
