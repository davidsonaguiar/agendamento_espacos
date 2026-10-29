from app.compartilhado.infra.banco_dados import SessaoBD
from app.compartilhado.infra.seguranca.codificador_senha import CodificadorSenha
from app.compartilhado.infra.seguranca.jwt import JWT
from app.modulos.usuarios.casos_uso.autenticar_usuario import AutenticarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.cadastrar_usuario import CadastrarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.listar_usuarios import ListarUsuariosCasoDeUso
from app.modulos.usuarios.infra.repositorios import UsuarioRepositorio


def pegar_caso_de_uso_cadastro(db: SessaoBD) -> CadastrarUsuarioCasoDeUso:
    repositorio = UsuarioRepositorio(db)
    codificador = CodificadorSenha()
    
    return CadastrarUsuarioCasoDeUso(
        repositorio=repositorio, 
        codificador=codificador
    )

def pegar_caso_de_uso_autenticacao(db: SessaoBD) -> AutenticarUsuarioCasoDeUso:
    return AutenticarUsuarioCasoDeUso(
        repositorio=UsuarioRepositorio(db),
        codificador=CodificadorSenha(),
        token_servico=JWT()
    )

def pegar_caso_de_uso_listar_usuarios(db: SessaoBD) -> ListarUsuariosCasoDeUso:
    return ListarUsuariosCasoDeUso(UsuarioRepositorio(db))
