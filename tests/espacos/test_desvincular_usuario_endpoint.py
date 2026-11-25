import pytest

from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco


def test_administrador_desvincula_usuario_do_espaco(
    client, headers, usuarios, espaco
):
    url = f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}"
    vinculo = client.post(
        url,
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )
    resposta = client.delete(url, headers=headers[PerfilUsuario.ADMINISTRADOR])

    assert vinculo.status_code == 201
    assert resposta.status_code == 200
    assert "removido" in resposta.json()["mensagem"]


def test_desvincular_usuario_rejeita_requisicao_sem_token(
    client, usuarios, espaco
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}"
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "perfil",
    [PerfilEspaco.MONITOR, PerfilUsuario.MEMBRO, PerfilUsuario.MEMBRO],
)
def test_desvincular_usuario_rejeita_perfil_sem_permissao(
    client, headers, usuarios, espaco, perfil
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[perfil],
    )

    assert resposta.status_code == 403


def test_desvincular_vinculo_inexistente_retorna_nao_encontrado(
    client, headers, usuarios, espaco
):
    resposta = client.delete(
        f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_desvincular_rejeita_espaco_inexistente(client, headers, usuarios):
    resposta = client.delete(
        f"/espacos/99999/usuarios/{usuarios[PerfilEspaco.MONITOR]}",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_coordenador_remove_monitor_do_proprio_espaco(
    client, headers, usuarios, espaco
):
    url = f"/espacos/{espaco['id']}/usuarios/{usuarios[PerfilEspaco.MONITOR]}"
    vinculo = client.post(
        url,
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"perfil_espaco": PerfilEspaco.MONITOR.value},
    )
    resposta = client.delete(
        url,
        headers=headers[PerfilEspaco.COORDENADOR],
    )

    assert vinculo.status_code == 201
    assert resposta.status_code == 200
