from typing import Annotated

from fastapi import Depends

from app.compartilhado.infra.banco_dados import SessaoBD
from app.compartilhado.infra.config import config
from app.compartilhado.infra.email import ResendEmailServico
from app.compartilhado.infra.seguranca.codificador_senha import CodificadorSenha
from app.compartilhado.infra.seguranca.jwt import JWT
from app.modulos.usuarios.casos_uso.autenticar_usuario import AutenticarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.alterar_senha import AlterarSenhaCasoDeUso
from app.modulos.usuarios.casos_uso.cadastrar_usuario import CadastrarUsuarioCasoDeUso
from app.modulos.usuarios.casos_uso.gerenciar_tokens import GerenciarTokensCasoDeUso
from app.modulos.usuarios.casos_uso.listar_usuarios import ListarUsuariosCasoDeUso
from app.modulos.usuarios.casos_uso.recuperar_senha import (
    RedefinirSenhaCasoDeUso,
    SolicitarRecuperacaoSenhaCasoDeUso,
)
from app.modulos.usuarios.infra.repositorios import (
    SessaoAutenticacaoRepositorio,
    TokenRedefinicaoSenhaRepositorio,
    UsuarioRepositorio,
)


def pegar_caso_de_uso_cadastro(db: SessaoBD) -> CadastrarUsuarioCasoDeUso:
    repositorio = UsuarioRepositorio(db)
    codificador = CodificadorSenha()
    
    return CadastrarUsuarioCasoDeUso(
        repositorio=repositorio, 
        codificador=codificador
    )

def pegar_caso_de_uso_autenticacao(db: SessaoBD) -> AutenticarUsuarioCasoDeUso:
    repositorio_usuario = UsuarioRepositorio(db)
    return AutenticarUsuarioCasoDeUso(
        repositorio=repositorio_usuario,
        codificador=CodificadorSenha(),
        tokens=GerenciarTokensCasoDeUso(
            sessoes=SessaoAutenticacaoRepositorio(db),
            usuarios=repositorio_usuario,
            token_servico=JWT(),
        ),
    )

def pegar_caso_de_uso_tokens(db: SessaoBD) -> GerenciarTokensCasoDeUso:
    return GerenciarTokensCasoDeUso(
        sessoes=SessaoAutenticacaoRepositorio(db),
        usuarios=UsuarioRepositorio(db),
        token_servico=JWT(),
    )

def pegar_caso_de_uso_alterar_senha(db: SessaoBD) -> AlterarSenhaCasoDeUso:
    return AlterarSenhaCasoDeUso(
        repositorio=UsuarioRepositorio(db),
        codificador=CodificadorSenha(),
    )

def pegar_caso_de_uso_listar_usuarios(db: SessaoBD) -> ListarUsuariosCasoDeUso:
    return ListarUsuariosCasoDeUso(UsuarioRepositorio(db))


def pegar_servico_email() -> ResendEmailServico:
    return ResendEmailServico()


def pegar_caso_de_uso_solicitar_recuperacao_senha(
    db: SessaoBD,
    servico_email: Annotated[
        ResendEmailServico, Depends(pegar_servico_email)
    ],
) -> SolicitarRecuperacaoSenhaCasoDeUso:
    return SolicitarRecuperacaoSenhaCasoDeUso(
        usuarios=UsuarioRepositorio(db),
        tokens=TokenRedefinicaoSenhaRepositorio(db),
        enviar_email=servico_email.enviar,
        url_frontend=config.url_frontend,
        minutos_validade_token=config.minutos_validade_token_recuperacao_senha,
    )


def pegar_caso_de_uso_redefinir_senha(
    db: SessaoBD,
) -> RedefinirSenhaCasoDeUso:
    return RedefinirSenhaCasoDeUso(
        tokens=TokenRedefinicaoSenhaRepositorio(db),
        codificador=CodificadorSenha(),
    )
