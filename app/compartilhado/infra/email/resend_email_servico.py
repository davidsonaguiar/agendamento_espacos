import resend

from app.compartilhado.infra.config import config


class ResendEmailServico:
    def enviar(self, destinatario: str, assunto: str, mensagem_html: str) -> None:
        if config.resend_api_key is None:
            raise RuntimeError("RESEND_API_KEY não está configurada.")

        resend.api_key = config.resend_api_key.get_secret_value()
        parametros: resend.Emails.SendParams = {
            "from": config.resend_from_email,
            "to": [destinatario],
            "subject": assunto,
            "html": mensagem_html,
        }
        resend.Emails.send(parametros)
