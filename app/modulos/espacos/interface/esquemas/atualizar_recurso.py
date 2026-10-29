from pydantic import BaseModel, Field, model_validator


class AtualizarRecurso(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    tipo: str | None = Field(None, min_length=1, max_length=100)
    autorizacao_necessaria: bool | None = None
    reserva_independente: bool | None = None

    @model_validator(mode="after")
    def validar_campos(self) -> "AtualizarRecurso":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        for campo in self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError(f"{campo} não pode ser nulo.")
        return self
