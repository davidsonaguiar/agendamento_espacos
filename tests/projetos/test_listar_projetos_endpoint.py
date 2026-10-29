from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.projetos.conftest import criar_projeto


def test_administrador_lista_todos_os_projetos(client, headers, usuarios):
    primeiro = criar_projeto(
        client, headers, usuarios[PerfilUsuario.SERVIDOR]
    )
    segundo = criar_projeto(
        client, headers, usuarios[PerfilUsuario.SERVIDOR]
    )

    resposta = client.get(
        "/projetos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert {primeiro["id"], segundo["id"]} <= ids_retornados


def test_servidor_lista_projetos_dos_quais_e_responsavel(client, headers, usuarios):
    projeto_responsavel = criar_projeto(
        client,
        headers,
        usuarios[PerfilUsuario.SERVIDOR],
        perfil_criador=PerfilUsuario.SERVIDOR,
    )
    projeto_de_outra_pessoa = criar_projeto(
        client, headers, usuarios[PerfilUsuario.COORDENADOR]
    )

    resposta = client.get(
        "/projetos/",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert projeto_responsavel["id"] in ids_retornados
    assert projeto_de_outra_pessoa["id"] not in ids_retornados


def test_aluno_lista_projetos_dos_quais_participa(client, headers, usuarios):
    projeto_participante = criar_projeto(
        client, headers, usuarios[PerfilUsuario.SERVIDOR]
    )
    projeto_sem_vinculo = criar_projeto(
        client, headers, usuarios[PerfilUsuario.SERVIDOR]
    )
    adicionar = client.post(
        f"/projetos/{projeto_participante['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "id_usuario": usuarios[PerfilUsuario.ALUNO],
            "papel_no_projeto": "Estudante",
        },
    )
    assert adicionar.status_code == 201

    resposta = client.get(
        "/projetos/",
        headers=headers[PerfilUsuario.ALUNO],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert projeto_participante["id"] in ids_retornados
    assert projeto_sem_vinculo["id"] not in ids_retornados


def test_listar_projetos_rejeita_requisicao_sem_token(client):
    resposta = client.get("/projetos/")

    assert resposta.status_code == 401
