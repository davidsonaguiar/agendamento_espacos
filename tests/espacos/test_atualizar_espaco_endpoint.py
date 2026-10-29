import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.COORDENADOR],
)
def test_perfil_autorizado_atualiza_espaco(client, headers, espaco, perfil):
    resposta = client.put(
        f"/espacos/{espaco['id']}",
        headers=headers[perfil],
        json={"descricao": "Descrição atualizada"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["descricao"] == "Descrição atualizada"


def test_atualizar_espaco_rejeita_requisicao_sem_token(client, espaco):
    resposta = client.put(
        f"/espacos/{espaco['id']}",
        json={"descricao": "Alteração não autorizada"},
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_atualizar_espaco_rejeita_perfil_sem_permissao(
    client, headers, espaco, perfil
):
    resposta = client.put(
        f"/espacos/{espaco['id']}",
        headers=headers[perfil],
        json={"descricao": "Alteração não autorizada"},
    )

    assert resposta.status_code == 403


def test_atualizar_espaco_inexistente_retorna_nao_encontrado(client, headers):
    resposta = client.put(
        "/espacos/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"descricao": "Descrição atualizada"},
    )

    assert resposta.status_code == 404


def test_atualizar_espaco_rejeita_nome_invalido(client, headers, espaco):
    resposta = client.put(
        f"/espacos/{espaco['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"nome": "ab"},
    )

    assert resposta.status_code == 422


def test_atualizar_espaco_rejeita_nome_duplicado(
    client, headers, espaco
):
    from tests.espacos.conftest import criar_espaco

    outro = criar_espaco(client, headers, nome="Outro espaço")
    resposta = client.put(
        f"/espacos/{espaco['id']}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"nome": outro["nome"]},
    )

    assert resposta.status_code == 409
