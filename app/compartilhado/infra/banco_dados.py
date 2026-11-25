from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.compartilhado.infra.config import config

motor = create_engine(config.url_banco_dados)

SessaoLocal = sessionmaker(
    bind=motor,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def pegar_banco_dados() -> Generator[Session, None, None]:
    db = SessaoLocal()

    try:
        yield db
    finally:
        db.close()


SessaoBD = Annotated[Session, Depends(pegar_banco_dados)]
