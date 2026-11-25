from pydantic import BaseModel

from app.modulos.espacos.dominio.entidades import PerfilEspaco


class VincularUsuario(BaseModel):
    perfil_espaco: PerfilEspaco
