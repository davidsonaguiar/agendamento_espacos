from pydantic import BaseModel, ConfigDict, Field

from .horario_funcionamento_resposta import HorarioFuncionamentoResposta
from .pausa_resposta import PausaResposta
from .recurso_resposta import RecursoResposta
from .usuario_vinculado_resposta import UsuarioVinculadoResposta


class EspacoResposta(BaseModel):
    id: int
    nome: str
    descricao: str | None
    capacidade: int | None
    bloco: str | None
    disponibilidade: bool
    recursos: list[RecursoResposta] = Field(default_factory=list)
    usuarios_vinculados: list[UsuarioVinculadoResposta] = Field(default_factory=list)
    horarios_funcionamento: list[HorarioFuncionamentoResposta] = Field(
        default_factory=list
    )
    pausas_funcionamento: list[PausaResposta] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
