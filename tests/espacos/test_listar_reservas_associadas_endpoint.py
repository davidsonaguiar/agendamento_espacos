from datetime import date, time, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.modulos.espacos.infra.modelos import EspacoHorarioFuncionamentoModelo
from app.modulos.usuarios.dominio.entidades import PerfilUsuario
from tests.agendamento.conftest import criar_solicitacao
from tests.espacos.conftest import criar_recurso


def configurar_horarios(
    test_session_factory: sessionmaker[Session], id_espaco: int
) -> None:
    with test_session_factory() as db:
        db.add_all(
            [
                EspacoHorarioFuncionamentoModelo(
                    id_espaco=id_espaco,
                    dia_semana=dia_semana,
                    hora_abertura=time(8),
                    hora_fechamento=time(17),
                    ativo=True,
                )
                for dia_semana in range(7)
            ]
        )
        db.commit()


def solicitar_recurso_independente(
    client, headers, id_recurso: int, data_reserva: date
):
    resposta = client.post(
        "/solicitacoes/",
        headers=headers[PerfilUsuario.SERVIDOR],
        json={
            "finalidade": "Utilização independente de recurso",
            "id_espaco": None,
            "ids_recursos": [id_recurso],
            "horarios": [
                {
                    "data_reserva": data_reserva.isoformat(),
                    "hora_inicio": "11:00",
                    "hora_fim": "12:00",
                }
            ],
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def aprovar_solicitacao(client, headers, solicitacao):
    resposta = client.patch(
        f"/solicitacoes/{solicitacao['id']}/decisao",
        headers=headers[PerfilUsuario.ADMINISTRADOR],
        json={
            "status": "Aprovado",
            "justificativa": "Reserva aprovada para teste.",
        },
    )
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


def test_listas_de_espacos_e_recursos_incluem_reservas_associadas(
    client, headers, espaco, test_session_factory
):
    configurar_horarios(test_session_factory, espaco["id"])
    recurso_compartilhado = criar_recurso(
        client,
        headers,
        espaco["id"],
        nome="Recurso reservado com o espaço",
        reserva_independente=False,
    )
    recurso_independente = criar_recurso(
        client,
        headers,
        espaco["id"],
        nome="Recurso reservado sozinho",
        reserva_independente=True,
    )
    data_espaco = date.today() + timedelta(days=14)
    data_recurso = data_espaco + timedelta(days=1)

    solicitacao_espaco = criar_solicitacao(
        client,
        headers,
        espaco["id"],
        ids_recursos=[recurso_compartilhado["id"]],
        horarios=[
            {
                "data_reserva": data_espaco.isoformat(),
                "hora_inicio": "10:00",
                "hora_fim": "11:00",
            }
        ],
    )
    aprovar_solicitacao(client, headers, solicitacao_espaco)

    solicitacao_recurso = solicitar_recurso_independente(
        client,
        headers,
        recurso_independente["id"],
        data_recurso,
    )
    aprovar_solicitacao(client, headers, solicitacao_recurso)

    espacos = client.get(
        "/espacos/",
        headers=headers[PerfilUsuario.SERVIDOR],
    )
    recursos = client.get(
        f"/espacos/{espaco['id']}/recursos",
        headers=headers[PerfilUsuario.SERVIDOR],
    )

    assert espacos.status_code == 200, espacos.text
    assert recursos.status_code == 200, recursos.text
    espaco_listado = next(
        item for item in espacos.json() if item["id"] == espaco["id"]
    )
    reservas_espaco = espaco_listado["reservas"]
    assert len(reservas_espaco) == 1
    assert reservas_espaco[0]["espaco_reservado"] is True

    recursos_listados = {item["id"]: item for item in recursos.json()}
    reserva_compartilhada = recursos_listados[recurso_compartilhado["id"]][
        "reservas"
    ]
    reserva_independente = recursos_listados[recurso_independente["id"]][
        "reservas"
    ]
    assert len(reserva_compartilhada) == 1
    assert reserva_compartilhada[0]["espaco_reservado"] is True
    assert len(reserva_independente) == 1
    assert reserva_independente[0]["espaco_reservado"] is False
    assert reserva_independente[0]["id_solicitacao"] == solicitacao_recurso["id"]

    recurso_aninhado = next(
        item
        for item in espaco_listado["recursos"]
        if item["id"] == recurso_independente["id"]
    )
    assert len(recurso_aninhado["reservas"]) == 1
    assert recurso_aninhado["reservas"][0]["espaco_reservado"] is False
