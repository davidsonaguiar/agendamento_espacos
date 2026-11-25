from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from app.modulos.espacos.dominio.entidades import PerfilEspaco
from tests.projetos.conftest import criar_projeto


def test_administrador_lista_todos_os_projetos(client, headers, usuarios):
    primeiro = criar_projeto(
        client, headers, usuarios[PerfilUsuario.MEMBRO]
    )
    segundo = criar_projeto(
        client, headers, usuarios[PerfilUsuario.MEMBRO]
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
        usuarios[PerfilUsuario.MEMBRO],
        perfil_criador=PerfilUsuario.MEMBRO,
    )
    projeto_de_outra_pessoa = criar_projeto(
        client, headers, usuarios[PerfilEspaco.COORDENADOR]
    )

    resposta = client.get(
        "/projetos/",
        headers=headers[PerfilUsuario.MEMBRO],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert projeto_responsavel["id"] in ids_retornados
    assert projeto_de_outra_pessoa["id"] not in ids_retornados


def test_aluno_lista_projetos_dos_quais_participa(client, headers, usuarios):
    projeto_participante = criar_projeto(
        client, headers, usuarios[PerfilEspaco.COORDENADOR]
    )
    projeto_sem_vinculo = criar_projeto(
        client, headers, usuarios[PerfilEspaco.MONITOR]
    )
    adicionar = client.post(
        f"/projetos/{projeto_participante['id']}/participantes",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "id_usuario": usuarios[PerfilUsuario.MEMBRO],
            "papel_no_projeto": "Estudante",
        },
    )
    assert adicionar.status_code == 201

    resposta = client.get(
        "/projetos/",
        headers=headers[PerfilUsuario.MEMBRO],
    )

    assert resposta.status_code == 200
    ids_retornados = {item["id"] for item in resposta.json()}
    assert projeto_participante["id"] in ids_retornados
    assert projeto_sem_vinculo["id"] not in ids_retornados


def test_listar_projetos_rejeita_requisicao_sem_token(client):
    resposta = client.get("/projetos/")

    assert resposta.status_code == 401
