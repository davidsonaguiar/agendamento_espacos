from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def test_responsavel_atualiza_projeto(client, headers, projeto):
    resposta = client.put(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={
            "finalidade": "Finalidade alterada pela API",
            "quantidade_participantes": 5,
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["finalidade"] == "Finalidade alterada pela API"
    assert resposta.json()["quantidade_participantes"] == 5


def test_usuario_que_nao_e_responsavel_nao_atualiza_projeto(
    client, headers, projeto
):
    resposta = client.put(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.COORDENADOR],
        json={"finalidade": "Alteração não autorizada"},
    )

    assert resposta.status_code == 403


def test_atualizar_projeto_inexistente_retorna_nao_encontrado(
    client, headers
):
    resposta = client.put(
        "/projetos/99999",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={"finalidade": "Projeto inexistente"},
    )

    assert resposta.status_code == 404


def test_atualizar_projeto_rejeita_payload_invalido(client, headers, projeto):
    resposta = client.put(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={"finalidade": None},
    )

    assert resposta.status_code == 422


def test_atualizar_projeto_aceita_payload_vazio_sem_alteracoes(
    client, headers, projeto
):
    resposta = client.put(
        f"/projetos/{projeto['id']}",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={},
    )

    assert resposta.status_code == 200


def test_atualizar_projeto_rejeita_requisicao_sem_token(client, projeto):
    resposta = client.put(
        f"/projetos/{projeto['id']}",
        json={"finalidade": "Sem token"},
    )

    assert resposta.status_code == 401
