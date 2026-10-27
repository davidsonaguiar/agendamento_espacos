from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.projetos.conftest import criar_projeto


def test_obter_projeto_com_perfil_de_gestao(client, headers, projeto):
    resposta = client.get(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.COORDENADOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["id"] == projeto["id"]


def test_servidor_obtem_projeto_quando_e_responsavel(client, headers, projeto):
    resposta = client.get(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    assert resposta.json()["id_responsavel"] == projeto["id_responsavel"]


def test_aluno_obtem_projeto_quando_e_participante(
    client, headers, usuarios, projeto
):
    adicionar = client.post(
        f"/projetos/{projeto['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "id_usuario": usuarios[PerfilUsuario.ALUNO],
            "papel_no_projeto": "Estudante",
        },
    )
    assert adicionar.status_code == 201

    resposta = client.get(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.ALUNO],
    )

    assert resposta.status_code == 200
    assert resposta.json()["id"] == projeto["id"]


def test_aluno_sem_vinculo_nao_obtem_projeto(client, headers, projeto):
    resposta = client.get(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.ALUNO],
    )
    assert resposta.status_code == 404


def test_obter_projeto_inexistente_retorna_nao_encontrado(client, headers):
    resposta = client.get(
        "/projetos/99999",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 404


def test_obter_projeto_rejeita_requisicao_sem_token(client, projeto):
    resposta = client.get(f"/projetos/{projeto['id']}")

    assert resposta.status_code == 401
