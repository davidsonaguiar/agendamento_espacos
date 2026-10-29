import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_administrador_vincula_monitor_ao_espaco(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 201
    assert "vinculado" in resposta.json()["mensagem"]


def test_coordenador_pode_vincular_usuario_ao_espaco(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 201


def test_vincular_usuario_rejeita_requisicao_sem_token(
    client, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}"
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilUsuario.MONITOR, PerfilUsuario.SERVIDOR, PerfilUsuario.ALUNO],
)
def test_vincular_usuario_rejeita_perfil_sem_permissao(
    client, headers, usuarios, espaco, perfil
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_vincular_usuario_rejeita_espaco_inexistente(
    client, headers, usuarios
):
    resposta = client.post(
        f"/espacos/99999/usuarios/{usuarios[PerfilUsuario.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_vincular_usuario_rejeita_usuario_inexistente(client, headers, espaco):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_vincular_usuario_rejeita_perfil_nao_vinculavel(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.SERVIDOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 403


def test_vincular_usuario_rejeita_vinculo_duplicado(
    client, headers, usuarios, espaco
):
    url = f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MONITOR]}"
    primeira = client.post(url, headers=headers[PerfilUsuario.ADMINISTRADOR])
    segunda = client.post(url, headers=headers[PerfilUsuario.ADMINISTRADOR])

    assert primeira.status_code == 201
    assert segunda.status_code == 409
