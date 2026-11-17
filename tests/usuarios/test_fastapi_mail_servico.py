from fastapi_mail import MessageType
from pydantic import SecretStr
import pytest

from app.compartilhado.infra.config import config
from app.compartilhado.infra.email import FastApiMailServico


def test_monta_mensagem_html_com_configuracao_smtp(monkeypatch):
    chamada = {}

    class FastMailFalso:
        def __init__(self, configuracao):
            chamada["configuracao"] = configuracao

        async def send_message(self, mensagem):
            chamada["mensagem"] = mensagem

    monkeypatch.setattr(
        "app.compartilhado.infra.email.fastapi_mail_servico.FastMail",
        FastMailFalso,
    )
    monkeypatch.setattr(config, "mail_username", "usuario@example.com")
    monkeypatch.setattr(config, "mail_password", SecretStr("senha"))
    monkeypatch.setattr(config, "mail_from", "usuario@example.com")
    monkeypatch.setattr(config, "mail_from_name", "Sistema")
    monkeypatch.setattr(config, "mail_server", "smtp.example.com")

    FastApiMailServico().enviar(
        "destinatario@example.com", "Assunto", "<p>Mensagem</p>"
    )

    assert chamada["configuracao"].MAIL_SERVER == "smtp.example.com"
    assert chamada["mensagem"].recipients[0].email == "destinatario@example.com"
    assert chamada["mensagem"].body == "<p>Mensagem</p>"
    assert chamada["mensagem"].subtype == MessageType.html


def test_sem_configuracao_smtp_falha_explicitamente(monkeypatch):
    monkeypatch.setattr(config, "mail_username", None)

    with pytest.raises(RuntimeError, match="SMTP"):
        FastApiMailServico().enviar(
            "destinatario@example.com", "Assunto", "<p>Mensagem</p>"
        )
