from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.compartilhado.infra.seguranca.codificador_senha import CodificadorSenha
from app.modulos.usuarios.infra.modelos import UsuarioModelo
from tests.conftest import cabecalhos_autenticacao
from app.modulos.usuarios.dominio.entidades import PerfilUsuario


def criar_espaco(client, headers, nome="Espaço de teste para agendamento"):
    resposta = client.post(
        "/espacos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={"nome": nome},
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_projeto(client, headers, id_responsavel):
    resposta = client.post(
        "/projetos/",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "descricao": "Projeto de teste",
            "finalidade": "Validar fluxo de agendamento",
            "id_responsavel": id_responsavel,
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def payload_solicitacao(espaco_id: int, **overrides):
    return {
        "tipo": "Espaço",
        "finalidade": "Atividade de integração",
        "urgencia": False,
        "id_espaco": espaco_id,
        "ids_usuarios_envolvidos": [],
        "horarios": [
            {
                "data_reserva": (date.today() + timedelta(days=30)).isoformat(),
                "hora_inicio": "10:00",
                "hora_fim": "12:00",
            }
        ],
    } | overrides


def criar_solicitacao(
    client,
    headers,
    id_espaco: int,
    *,
    id_projeto: int | None = None,
    perfil=PerfilUsuario.SERVIDOR,
    cabecalho=None,
    **overrides,
):
    payload = payload_solicitacao(id_espaco, **overrides)
    if id_projeto is not None:
        payload["id_projeto"] = id_projeto
    resposta = client.post(
        "/solicitacoes/",
        headers=cabecalho or headers[perfil],
        json=payload,
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.fixture
def espaco(client, headers):
    return criar_espaco(client, headers)


@pytest.fixture
def projeto(client, headers, usuarios):
    return criar_projeto(
        client,
        headers,
        usuarios[PerfilUsuario.SERVIDOR],
    )


@pytest.fixture
def solicitacao(client, headers, espaco):
    return criar_solicitacao(client, headers, espaco["id"])


@pytest.fixture
def anexo(client, headers, solicitacao):
    resposta = client.post(
        f"/solicitacoes/{solicitacao['id']}/anexos",
        headers=headers[PerfilUsuario.SERVIDOR],
        files={
            "arquivo": (
                "documento.pdf",
                b"%PDF-1.7 endpoint test",
                "application/pdf",
            )
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.fixture
def outro_servidor(
    test_session_factory: sessionmaker[Session],
) -> dict:
    senha_codificada = CodificadorSenha().codificar_senha("SenhaValida123!")
    with test_session_factory() as db:
        usuario = UsuarioModelo(
            nome_completo="Outro servidor",
            cpf="99999999999",
            vinculo_institucional="MAT99999",
            email="outro.servidor@example.com",
            senha_codificada=senha_codificada,
            perfil=PerfilUsuario.SERVIDOR,
            ativo=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return {
            "id": usuario.id,
            "headers": cabecalhos_autenticacao(usuario.id),
        }
