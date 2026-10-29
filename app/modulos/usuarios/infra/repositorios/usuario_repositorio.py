from sqlalchemy.orm import Session

from app.modulos.usuarios.dominio.contratos import UsuarioRepositorioContrato
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario
from app.modulos.usuarios.infra.modelos import UsuarioModelo


class UsuarioRepositorio(UsuarioRepositorioContrato):
    def __init__(self, db: Session):
        self.db = db

    def listar(
        self,
        perfil: PerfilUsuario | None = None,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Usuario]:
        consulta = self.db.query(UsuarioModelo)

        if perfil:
            consulta = consulta.filter(UsuarioModelo.perfil == perfil)

        if ativo is not None:
            consulta = consulta.filter(UsuarioModelo.ativo == ativo)

        modelos = consulta.offset(skip).limit(limit).all()
        return [Usuario.model_validate(modelo) for modelo in modelos]

    def buscar_por_id(self, id_usuario: int) -> Usuario | None:
        modelo = (
            self.db.query(UsuarioModelo).filter(UsuarioModelo.id == id_usuario).first()
        )
        if not modelo:
            return None
        return Usuario.model_validate(modelo)

    def buscar_por_cpf(self, cpf: str) -> Usuario | None:
        modelo = self.db.query(UsuarioModelo).filter(UsuarioModelo.cpf == cpf).first()
        if not modelo:
            return None
        return Usuario.model_validate(modelo)

    def buscar_por_email(self, email: str) -> Usuario | None:
        modelo = (
            self.db.query(UsuarioModelo).filter(UsuarioModelo.email == email).first()
        )
        if not modelo:
            return None
        return Usuario.model_validate(modelo)

    def buscar_por_vinculo(self, vinculo_institucional: str) -> Usuario | None:
        modelo = (
            self.db.query(UsuarioModelo)
            .filter(UsuarioModelo.vinculo_institucional == vinculo_institucional)
            .first()
        )
        if not modelo:
            return None
        return Usuario.model_validate(modelo)

    def salvar(self, usuario: UsuarioModelo) -> Usuario:
        usuario_modelo = UsuarioModelo(
            nome_completo=usuario.nome_completo,
            cpf=usuario.cpf,
            vinculo_institucional=usuario.vinculo_institucional,
            email=usuario.email,
            senha_codificada=usuario.senha_codificada,
            perfil=usuario.perfil,
            ativo=usuario.ativo,
        )

        self.db.add(usuario_modelo)
        self.db.commit()
        self.db.refresh(usuario_modelo)

        return Usuario.model_validate(usuario_modelo)
