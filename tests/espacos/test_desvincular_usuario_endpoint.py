import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_administrador_desvincula_usuario_do_espaco(
    client, headers, usuarios, espaco
):
    url = f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}"
    vinculo = client.post(url, headers=headers[PerfilUsuario.ADMINISTRADOR])
    resposta = client.delete(url, headers=headers[PerfilUsuario.ADMINISTRADOR])

    assert vinculo.status_code == 201
    assert resposta.status_code == 200
    assert "removido" in resposta.json()["mensagem"]


def test_desvincular_usuario_rejeita_requisicao_sem_token(
    client, usuarios, espaco
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}"
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_desvincular_usuario_rejeita_perfil_sem_permissao(
    client, headers, usuarios, espaco, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_desvincular_vinculo_inexistente_retorna_nao_encontrado(
    client, headers, usuarios, espaco
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_desvincular_rejeita_espaco_inexistente(client, headers, usuarios):
    resposta = client.delete(
        f"/espacos/99999/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404
