from app.compartilhado.dominio.erros import AcessoNegadoErro, CredenciaisInvalidasErro
from app.modulos.usuarios.dominio.contratos import (
    CodificadorSenhaContrato,
    UsuarioRepositorioContrato,
)
from app.modulos.usuarios.dominio.entidades import Usuario
from app.modulos.usuarios.casos_uso.gerenciar_tokens import (
    GerenciarTokensCasoDeUso,
)
from app.modulos.usuarios.interface.esquemas import TokenResposta, UsuarioLogin


class AutenticarUsuarioCasoDeUso:
    def __init__(
        self,
        repositorio: UsuarioRepositorioContrato,
        codificador: CodificadorSenhaContrato,
        tokens: GerenciarTokensCasoDeUso,
    ):
        self.repositorio = repositorio
        self.codificador = codificador
        self.tokens = tokens

    def executar(self, dados: UsuarioLogin) -> tuple[TokenResposta, str]:
        usuario = self._pegar_usuario_por_identificacao(dados.identificacao)
        self._validar_usuario(usuario, dados.senha.get_secret_value())
        return self.tokens.emitir(usuario)

    def _pegar_usuario_por_identificacao(self, identificacao: str) -> Usuario | None:
        if "@" in identificacao:
            return self.repositorio.buscar_por_email(identificacao)

        cpf_limpo = identificacao.replace(".", "").replace("-", "")
        return self.repositorio.buscar_por_cpf(cpf_limpo)
    

    def _validar_usuario(self, usuario: Usuario | None, senha: str) -> None:
        if not usuario or not self.codificador.verificar_senha(
            senha=senha,
            senha_codificada=usuario.senha_codificada,
        ):
            raise CredenciaisInvalidasErro()

        if not usuario.ativo:
            raise AcessoNegadoErro("Usuário inativo. Procure a coordenação do COLAB.")
