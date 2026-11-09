from app.compartilhado.dominio.erros import CredenciaisInvalidasErro
from app.modulos.usuarios.dominio.contratos import (
    CodificadorSenhaContrato,
    UsuarioRepositorioContrato,
)
from app.modulos.usuarios.dominio.entidades import Usuario
from app.modulos.usuarios.interface.esquemas import AlterarSenha


class AlterarSenhaCasoDeUso:
    def __init__(
        self,
        repositorio: UsuarioRepositorioContrato,
        codificador: CodificadorSenhaContrato,
    ):
        self.repositorio = repositorio
        self.codificador = codificador

    def executar(self, usuario: Usuario, dados: AlterarSenha) -> None:
        senha_atual = dados.senha_atual.get_secret_value()
        if not self.codificador.verificar_senha(
            senha=senha_atual,
            senha_codificada=usuario.senha_codificada,
        ):
            raise CredenciaisInvalidasErro()

        senha_nova = self.codificador.codificar_senha(
            dados.nova_senha.get_secret_value()
        )
        self.repositorio.atualizar_senha(usuario.id, senha_nova)
