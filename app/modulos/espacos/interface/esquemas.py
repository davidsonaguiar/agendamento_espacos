from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class CriarEspaco(BaseModel):
    nome: str = Field(..., min_length=3, description="Nome da sala ou laboratório (ex: COLAB Maker)")
    descricao: str | None = Field(None, description="Descrição dos equipamentos ou finalidade do espaço")
    capacidade: int | None = Field(None, description="Capacidade máxima de pessoas (ex: 20 pessoas)")
    bloco: str | None = Field(None, description="Localização física no campus (ex: Bloco de Informática)")
    disponibilidade: bool = Field(True, description="Indica se o espaço está ativo para uso")

class AtualizarEspaco(BaseModel):
    nome: str | None = Field(None, min_length=3, description="Novo nome da sala")
    descricao: str | None = Field(None, description="Nova descrição")
    capacidade: int | None = Field(None, description="Nova capacidade")
    bloco: str | None = Field(None, description="Novo bloco")

class EspacoResposta(BaseModel):
    id: int
    nome: str
    descricao: str | None
    capacidade: int | None
    bloco: str | None
    disponibilidade: bool

    model_config = ConfigDict(from_attributes=True)

class AtualizarHorario(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6, description="0=Domingo, 1=Segunda, ..., 6=Sábado")
    hora_abertura: time = Field(..., description="Horário de abertura, ex: 08:00")
    hora_fechamento: time = Field(..., description="Horário de fechamento, ex: 18:00")
    ativo: bool = Field(..., description="Define se o laboratório funciona neste dia específico")


class HorarioFuncionamentoResposta(BaseModel):
    id: int
    dia_semana: int
    hora_abertura: time
    hora_fechamento: time
    ativo: bool
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)


class CriarPausaFuncionamento(BaseModel):
    data_inicio: date
    data_fim: date
    motivo: str = Field(..., min_length=3, description="Ex: Manutenção da serra, Feriado nacional")

class PausaResposta(BaseModel):
    id: int
    data_inicio: date
    data_fim: date
    motivo: str
    id_espaco: int

    model_config = ConfigDict(from_attributes=True)
    