from app.compartilhado.dominio.entidade_base import EntidadeBase


class ParticipanteProjeto(EntidadeBase):
    id_usuario: int
    id_projeto: int
    nome_completo: str
    papel_no_projeto: str
