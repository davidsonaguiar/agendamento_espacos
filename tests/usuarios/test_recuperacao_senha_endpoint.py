from datetime import UTC, datetime, timedelta
from hashlib import sha256
from urllib.parse import parse_qs, unquote, urlparse

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.usuarios.interface.dependencias import pegar_servico_email
from app.modulos.usuarios.infra.modelos import TokenRedefinicaoSenhaModelo
from main import app


class EmailFalso:
    def __init__(self) -> None:
        self.mensagens: list[tuple[str, str, str]] = []

    def enviar(self, destinatario: str, assunto: str, mensagem_html: str) -> None:
        self.mensagens.append((destinatario, assunto, mensagem_html))


def test_solicitacao_nao_revela_se_email_existe(client, usuarios, monkeypatch):
    assert usuarios[PerfilUsuario.MEMBRO]
    email_falso = EmailFalso()
    monkeypatch.setitem(
        app.dependency_overrides, pegar_servico_email, lambda: email_falso
    )

    existente = client.post(
        "/usuarios/recuperar-senha", json={"email": "membro@example.com"}
    )
    inexistente = client.post(
        "/usuarios/recuperar-senha", json={"email": "ausente@example.com"}
    )

    assert existente.status_code == inexistente.status_code == 202
    assert existente.json() == inexistente.json()
    assert len(email_falso.mensagens) == 1
    assert email_falso.mensagens[0][0] == "membro@example.com"


def test_token_redefine_senha_uma_vez_e_revoga_sessao(
    client, usuarios, monkeypatch
):
    assert usuarios[PerfilUsuario.MEMBRO]
    email_falso = EmailFalso()
    monkeypatch.setitem(
        app.dependency_overrides, pegar_servico_email, lambda: email_falso
    )
    login = client.post(
        "/usuarios/login",
        json={"identificacao": "membro@example.com", "senha": "SenhaValida123!"},
    )
    assert login.status_code == 200

    resposta = client.post(
        "/usuarios/recuperar-senha", json={"email": "membro@example.com"}
    )
    assert resposta.status_code == 202
    html = email_falso.mensagens[0][2]
    link = unquote(html.split('href="', 1)[1].split('"', 1)[0])
    token = parse_qs(urlparse(link).query)["token"][0]

    redefinicao = client.post(
        "/usuarios/redefinir-senha",
        json={"token": token, "nova_senha": "SenhaNova123!"},
    )
    assert redefinicao.status_code == 204

    repetida = client.post(
        "/usuarios/redefinir-senha",
        json={"token": token, "nova_senha": "OutraSenha123!"},
    )
    assert repetida.status_code == 400
    assert client.post("/usuarios/refresh").status_code == 401

    novo_login = client.post(
        "/usuarios/login",
        json={"identificacao": "membro@example.com", "senha": "SenhaNova123!"},
    )
    assert novo_login.status_code == 200


def test_token_expirado_nao_redefine_senha(
    client, usuarios, test_session_factory
):
    token = "t" * 43
    agora = datetime.now(UTC)
    with test_session_factory() as db:
        db.add(
            TokenRedefinicaoSenhaModelo(
                id_usuario=usuarios[PerfilUsuario.MEMBRO],
                hash_token=sha256(token.encode("utf-8")).hexdigest(),
                criado_em=agora - timedelta(minutes=31),
                expira_em=agora - timedelta(minutes=1),
            )
        )
        db.commit()

    resposta = client.post(
        "/usuarios/redefinir-senha",
        json={"token": token, "nova_senha": "SenhaNova123!"},
    )
    assert resposta.status_code == 400
