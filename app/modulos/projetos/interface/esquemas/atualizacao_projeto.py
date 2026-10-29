from pydantic import BaseModel, Field, model_validator


class AtualizacaoProjeto(BaseModel):
    descricao: str | None = Field(None, min_length=3, max_length=255)
    finalidade: str | None = Field(None, min_length=3, max_length=255)
    quantidade_participantes: int | None = Field(None, ge=0)
    documentacao_base: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def validar_campos_obrigatorios(self) -> "AtualizacaoProjeto":
        for campo in ("descricao", "finalidade"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"{campo} não pode ser nulo.")
        return self
