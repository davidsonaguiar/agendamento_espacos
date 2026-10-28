from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao


def test_solicitante_obtem_url_assinada_do_anexo(
    client, headers, solicitacao, anexo
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}/anexos/{anexo['id']}/url",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["url_assinada"].startswith("https://storage.test/")
    assert resposta.json()["validade_segundos"] == 600


def test_administrador_obtem_url_assinada_de_anexo_alheio(
    client, headers, solicitacao, anexo
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}/anexos/{anexo['id']}/url",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200


def test_coordenador_obtem_url_assinada_de_anexo_alheio(
    client, headers, solicitacao, anexo
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}/anexos/{anexo['id']}/url",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 200


def test_usuario_sem_permissao_nao_obtem_url_de_anexo_alheio(
    client, headers, solicitacao, anexo
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}/anexos/{anexo['id']}/url",
        headers=headers[PerfilUsuario.MONITOR],
    )

    assert resposta.status_code == 403


def test_obter_url_rejeita_solicitacao_inexistente(client, headers, anexo):
    resposta = client.get(
        f"/solicitacoes/99999/anexos/{anexo['id']}/url",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_obter_url_rejeita_anexo_inexistente(client, headers, solicitacao):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}/anexos/99999/url",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_obter_url_rejeita_requisicao_sem_token(
    client, solicitacao, anexo
):
    resposta = client.get(
        f"/solicitacoes/{solicitacao['id']}/anexos/{anexo['id']}/url"
    )

    assert resposta.status_code == 401


def test_anexo_de_outra_solicitacao_nao_pode_ser_consultado(
    client, headers, espaco, outro_servidor, anexo
):
    outra_solicitacao = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        cabecalho=outro_servidor["headers"],
    )
    resposta = client.get(
        f"/solicitacoes/{outra_solicitacao['id']}/anexos/{anexo['id']}/url",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404
