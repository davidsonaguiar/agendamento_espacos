from pydantic import BaseModel, ConfigDict

from app.modulos.espacos.dominio.entidades import PerfilEspaco


class UsuarioVinculadoResposta(BaseModel):
    id_usuario: int
    nome_completo: str
    perfil_espaco: PerfilEspaco | None = None

    model_config = ConfigDict(from_attributes=True)
