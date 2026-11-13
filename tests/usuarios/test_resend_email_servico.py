import resend
from pydantic import SecretStr
import pytest

from app.compartilhado.infra.config import config
from app.compartilhado.infra.email import ResendEmailServico


def test_envia_email_com_a_configuracao_do_resend(monkeypatch):
    chamada = {}

    def enviar(parametros):
        chamada["parametros"] = parametros
        return {"id": "email-id"}

    monkeypatch.setattr(config, "resend_api_key", SecretStr("chave-teste"))
    monkeypatch.setattr(config, "resend_from_email", "Teste <teste@example.com>")
    monkeypatch.setattr(resend.Emails, "send", enviar)

    ResendEmailServico().enviar(
        "destinatario@example.com", "Assunto", "<p>Mensagem</p>"
    )

    assert resend.api_key == "chave-teste"
    assert chamada["parametros"] == {
        "from": "Teste <teste@example.com>",
        "to": ["destinatario@example.com"],
        "subject": "Assunto",
        "html": "<p>Mensagem</p>",
    }


def test_sem_api_key_falha_explicitamente(monkeypatch):
    monkeypatch.setattr(config, "resend_api_key", None)

    with pytest.raises(RuntimeError, match="RESEND_API_KEY"):
        ResendEmailServico().enviar(
            "destinatario@example.com", "Assunto", "<p>Mensagem</p>"
        )
