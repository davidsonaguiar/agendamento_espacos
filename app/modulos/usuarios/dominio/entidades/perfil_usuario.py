from enum import Enum


class PerfilUsuario(str, Enum):
    ADMINISTRADOR = "Administrador"
    MEMBRO = "Membro"
