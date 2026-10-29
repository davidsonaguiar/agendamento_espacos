from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modulos.agendamento.dominio.entidades import TipoSolicitacao

from .novo_horario_solicitacao import NovoHorarioSolicitacao


class NovaSolicitacao(BaseModel):
    tipo: TipoSolicitacao
    finalidade: str = Field(..., min_length=3, max_length=255)
    urgencia: bool = False
    id_projeto: int | None = Field(None, gt=0)
    id_espaco: int = Field(..., gt=0)
    ids_recursos: list[int] = Field(default_factory=list)
    ids_usuarios_envolvidos: list[int] = Field(default_factory=list)
    horarios: list[NovoHorarioSolicitacao] = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")

    @field_validator("ids_usuarios_envolvidos")
    @classmethod
    def validar_usuarios_envolvidos(cls, ids: list[int]) -> list[int]:
        if any(id_usuario <= 0 for id_usuario in ids):
            raise ValueError("Os IDs dos usuários envolvidos devem ser positivos.")
        if len(ids) != len(set(ids)):
            raise ValueError("Não informe usuários envolvidos duplicados.")
        return ids

    @field_validator("ids_recursos")
    @classmethod
    def validar_recursos(cls, ids: list[int]) -> list[int]:
        if any(id_recurso <= 0 for id_recurso in ids):
            raise ValueError("Os IDs dos recursos devem ser positivos.")
        if len(ids) != len(set(ids)):
            raise ValueError("Não informe recursos duplicados.")
        return ids
