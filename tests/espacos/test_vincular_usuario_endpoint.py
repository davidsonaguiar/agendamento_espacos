import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco


def test_administrador_vincula_monitor_ao_espaco(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 201
    assert "vinculado" in resposta.json()["mensagem"]


def test_coordenador_pode_vincular_usuario_ao_espaco(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 201


def test_coordenador_nao_pode_vincular_usuario_a_outro_espaco(
    client, headers, usuarios, espaco
):
    resposta_outro_espaco = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"nome": "Outro espaço"},
    )
    assert resposta_outro_espaco.status_code == 201
    outro_espaco = resposta_outro_espaco.json()

    resposta = client.post(
        f"/espacos/{outro_espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 403


def test_vincular_usuario_rejeita_requisicao_sem_token(
    client, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilEspaco.MONITOR, PerfilUsuario.MEMBRO],
)
def test_vincular_usuario_rejeita_perfil_sem_permissao(
    client, headers, usuarios, espaco, perfil
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[perfil],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 403


def test_vincular_usuario_rejeita_espaco_inexistente(
    client, headers, usuarios
):
    resposta = client.post(
        f"/espacos/99999/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 404


def test_vincular_usuario_rejeita_usuario_inexistente(client, headers, espaco):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 404


def test_vincular_usuario_rejeita_perfil_nao_vinculavel(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.ADMINISTRADOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )

    assert resposta.status_code == 403


def test_vincular_usuario_rejeita_vinculo_duplicado(
    client, headers, usuarios, espaco
):
    url = f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}"
    dados = {"perfil_espaco": PerfilEspaco.MONITOR.value}
    primeira = client.post(url, headers=headers[PerfilUsuario.ADMINISTRADOR], json=dados)
    segunda = client.post(url, headers=headers[PerfilUsuario.ADMINISTRADOR], json=dados)

    assert primeira.status_code == 201
    assert segunda.status_code == 409


def test_apenas_administrador_pode_vincular_coordenador(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MEMBRO]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.COORDENADOR.value},
    )

    assert resposta.status_code == 201


def test_coordenador_nao_pode_vincular_outro_coordenador(
    client, headers, usuarios, espaco
):
    resposta = client.post(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilUsuario.MEMBRO]}",
        headers=headers[PerfilEspaco.COORDENADOR],
        json={"perfil_espaco": PerfilEspaco.COORDENADOR.value},
    )

    assert resposta.status_code == 403
