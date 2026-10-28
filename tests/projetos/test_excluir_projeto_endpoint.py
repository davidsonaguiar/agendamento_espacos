from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.projetos.conftest import criar_projeto


def test_criador_exclui_projeto(client, headers, usuarios):
    projeto = criar_projeto(
        client,
        headers,
        usuarios[PerfilUsuario.SERVIDOR],
        perfil_criador=PerfilUsuario.SERVIDOR,
    )

    resposta = client.delete(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 204
    assert resposta.content == b""


def test_administrador_exclui_projeto_de_outro_criador(client, headers, projeto):
    resposta = client.delete(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 204


def test_usuario_que_nao_e_criador_nao_exclui_projeto(
    client, headers, projeto
):
    resposta = client.delete(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 403


def test_excluir_projeto_inexistente_retorna_nao_encontrado(client, headers):
    resposta = client.delete(
        "/projetos/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_excluir_projeto_rejeita_requisicao_sem_token(client, projeto):
    resposta = client.delete(f"/projetos/{projeto['id']}")

    assert resposta.status_code == 401
