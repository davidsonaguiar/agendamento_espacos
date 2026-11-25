import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.compartilhado.infra.config import config


class FastApiMailServico:
    def enviar(self, destinatario: str, assunto: str, mensagem_html: str) -> None:
        if (
            config.mail_username is None
            or config.mail_password is None
            or config.mail_server is None
        ):
            raise RuntimeError(
                "As configurações de SMTP do e-mail não estão completas."
            )

        configuracao = ConnectionConfig(
            MAIL_USERNAME=config.mail_username,
            MAIL_PASSWORD=config.mail_password.get_secret_value(),
            MAIL_FROM=config.mail_from or config.mail_username,
            MAIL_PORT=config.mail_port,
            MAIL_SERVER=config.mail_server,
            MAIL_FROM_NAME=config.mail_from_name,
            MAIL_STARTTLS=config.mail_starttls,
            MAIL_SSL_TLS=config.mail_ssl_tls,
            USE_CREDENTIALS=config.mail_use_credentials,
            VALIDATE_CERTS=config.mail_validate_certs,
        )
        mensagem = MessageSchema(
            subject=assunto,
            recipients=[destinatario],
            body=mensagem_html,
            subtype=MessageType.html,
        )
        asyncio.run(FastMail(configuracao).send_message(mensagem))

