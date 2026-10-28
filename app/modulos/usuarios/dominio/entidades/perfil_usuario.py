from enum import Enum


class PerfilUsuario(str, Enum):
    ADMINISTRADOR = "Administrador"
    COORDENADOR = "Coordenador"
    SERVIDOR = "Servidor"
    MONITOR = "Monitor"
    ALUNO = "Aluno"
