from pydantic import BaseModel, ConfigDict, Field, field_validator

from .novo_horario_solicitacao import NovoHorarioSolicitacao


class MensagemSolicitacao(BaseModel):
    mensagem: str = Field(..., min_length=3, max_length=2000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("mensagem")
    @classmethod
    def validar_mensagem(cls, valor: str) -> str:
        mensagem = valor.strip()
        if len(mensagem) < 3:
            raise ValueError("A mensagem deve conter ao menos 3 caracteres.")
        return mensagem


class ProporReplanejamento(MensagemSolicitacao):
    horarios: list[NovoHorarioSolicitacao] = Field(..., min_length=1)
    ids_recursos: list[int] = Field(default_factory=list)

    @field_validator("ids_recursos")
    @classmethod
    def validar_recursos(cls, valores: list[int]) -> list[int]:
        if any(id_recurso <= 0 for id_recurso in valores):
            raise ValueError("Os IDs dos recursos devem ser positivos.")
        if len(valores) != len(set(valores)):
            raise ValueError("Não informe recursos duplicados.")
        return valores


class ResponderProposta(MensagemSolicitacao):
    aceita: bool
