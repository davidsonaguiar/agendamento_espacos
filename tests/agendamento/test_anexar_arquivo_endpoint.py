from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from app.modulos.agendamento.casos_uso.anexar_arquivo import LIMITE_ANEXO_BYTES
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao


def test_solicitante_anexa_pdf_valido(
    client, headers, solicitacao, fake_storage
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={
            "arquivo": (
                "documento.pdf",
                b"%PDF-1.7 arquivo de teste",
                "application/pdf",
            )
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome_arquivo"] == "documento.pdf"
    assert resposta.json()["tipo_arquivo"] == "application/pdf"
    assert fake_storage.arquivos


def test_solicitante_anexa_docx_valido(client, headers, solicitacao):
    arquivo_docx = BytesIO()
    with ZipFile(arquivo_docx, "w", ZIP_DEFLATED) as documento:
        documento.writestr("[Content_Types].xml", "<Types/>")
        documento.writestr("word/document.xml", "<document/>")
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={
            "arquivo": (
                "documento.docx",
                arquivo_docx.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["tipo_arquivo"] == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_anexar_arquivo_rejeita_extensao_nao_permitida(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={"arquivo": ("script.exe", b"conteudo", "application/octet-stream")},
    )

    assert resposta.status_code == 422


def test_anexar_arquivo_rejeita_pdf_com_conteudo_invalido(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={"arquivo": ("documento.pdf", b"nao e pdf", "application/pdf")},
    )

    assert resposta.status_code == 422


def test_anexar_arquivo_rejeita_arquivo_vazio(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={"arquivo": ("documento.pdf", b"", "application/pdf")},
    )

    assert resposta.status_code == 422


def test_anexar_arquivo_rejeita_arquivo_acima_do_limite(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={
            "arquivo": (
                "documento.pdf",
                b"%PDF-" + b"x" * LIMITE_ANEXO_BYTES,
                "application/pdf",
            )
        },
    )

    assert resposta.status_code == 413


def test_anexar_arquivo_permite_somente_perfil_servidor(
    client, headers, solicitacao
):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        files={"arquivo": ("documento.pdf", b"%PDF-1.7", "application/pdf")},
    )

    assert resposta.status_code == 403


def test_anexar_arquivo_rejeita_usuario_diferente_do_solicitante(
    client, headers, espaco, outro_servidor
):
    solicitacao = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        cabecalho=outro_servidor["headers"],
    )
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={"arquivo": ("documento.pdf", b"%PDF-1.7", "application/pdf")},
    )

    assert resposta.status_code == 403


def test_anexar_arquivo_rejeita_solicitacao_inexistente(client, headers):
    resposta = client.post(
        "/solicitacoes/99999/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={"arquivo": ("documento.pdf", b"%PDF-1.7", "application/pdf")},
    )

    assert resposta.status_code == 404


def test_anexar_arquivo_rejeita_requisicao_sem_token(client, solicitacao):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        files={"arquivo": ("documento.pdf", b"%PDF-1.7", "application/pdf")},
    )

    assert resposta.status_code == 401
