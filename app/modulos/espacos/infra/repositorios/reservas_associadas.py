from collections import defaultdict

from sqlalchemy.orm import Session, selectinload

from app.modulos.espacos.dominio.entidades import ReservaAssociada


def _buscar_reservas(db: Session, *, ids_espacos=None, ids_recursos=None):
    from app.modulos.agendamento.infra.modelos import ReservaAgendaModelo
    from app.modulos.espacos.infra.modelos import RecursoModelo

    consulta = db.query(ReservaAgendaModelo).options(
        selectinload(ReservaAgendaModelo.recursos)
    ).filter(ReservaAgendaModelo.situacao == "Confirmada")
    if ids_espacos is not None:
        consulta = consulta.filter(ReservaAgendaModelo.id_espaco.in_(ids_espacos))
    if ids_recursos is not None:
        consulta = consulta.filter(
            ReservaAgendaModelo.recursos.any(RecursoModelo.id.in_(ids_recursos))
        )
    return consulta.order_by(
        ReservaAgendaModelo.data_hora_inicio,
        ReservaAgendaModelo.id,
    ).all()


def _converter(modelo) -> ReservaAssociada:
    return ReservaAssociada(
        id=modelo.id,
        data_hora_inicio=modelo.data_hora_inicio,
        data_hora_fim=modelo.data_hora_fim,
        situacao=modelo.situacao,
        id_solicitacao=modelo.id_solicitacao,
        id_espaco=modelo.id_espaco,
        espaco_reservado=modelo.espaco_reservado,
        ids_recursos=[recurso.id for recurso in modelo.recursos],
    )


def listar_reservas_por_espacos(
    db: Session, ids_espacos: list[int]
) -> tuple[dict[int, list[ReservaAssociada]], dict[int, list[ReservaAssociada]]]:
    reservas_por_espaco: dict[int, list[ReservaAssociada]] = defaultdict(list)
    reservas_por_recurso: dict[int, list[ReservaAssociada]] = defaultdict(list)
    if not ids_espacos:
        return reservas_por_espaco, reservas_por_recurso

    for modelo in _buscar_reservas(db, ids_espacos=ids_espacos):
        reserva = _converter(modelo)
        if modelo.espaco_reservado:
            reservas_por_espaco[modelo.id_espaco].append(reserva)
        for recurso in modelo.recursos:
            reservas_por_recurso[recurso.id].append(reserva)
    return reservas_por_espaco, reservas_por_recurso


def listar_reservas_por_recursos(
    db: Session, ids_recursos: list[int]
) -> dict[int, list[ReservaAssociada]]:
    reservas_por_recurso: dict[int, list[ReservaAssociada]] = defaultdict(list)
    if not ids_recursos:
        return reservas_por_recurso

    for modelo in _buscar_reservas(db, ids_recursos=ids_recursos):
        reserva = _converter(modelo)
        for recurso in modelo.recursos:
            if recurso.id in ids_recursos:
                reservas_por_recurso[recurso.id].append(reserva)
    return reservas_por_recurso
