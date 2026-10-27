from dataclasses import dataclass

from app.compartilhado.dominio.erros import (
    EntidadeNaoEncontradaErro,
    RegraDeNegocioErro,
)
from app.modulos.agendamento.dominio.contratos import (
    SolicitacaoRepositorioContrato,
)
from app.modulos.agendamento.dominio.entidades import (
    HorarioSolicitacao,
    Solicitacao,
    TipoSolicitacao,
    UsuarioEnvolvido,
)
from app.modulos.espacos.dominio.contratos import EspacoRepositorioContrato
from app.modulos.projetos.dominio.contratos import ProjetoRepositorioContrato
from app.modulos.usuarios.dominio.contratos import UsuarioRepositorioContrato


@dataclass
class DadosNovaSolicitacao:
    tipo: TipoSolicitacao
    finalidade: str
    urgencia: bool
    id_projeto: int | None
    id_espaco: int
    ids_usuarios_envolvidos: list[int]
    horarios: list[HorarioSolicitacao]


class CriarSolicitacaoCasoDeUso:
    def __init__(
        self,
        repositorio_solicitacao: SolicitacaoRepositorioContrato,
        repositorio_projeto: ProjetoRepositorioContrato,
        repositorio_espaco: EspacoRepositorioContrato,
        repositorio_usuario: UsuarioRepositorioContrato,
    ):
        self.repositorio_solicitacao = repositorio_solicitacao
        self.repositorio_projeto = repositorio_projeto
        self.repositorio_espaco = repositorio_espaco
        self.repositorio_usuario = repositorio_usuario

    def executar(
        self, dados: DadosNovaSolicitacao, id_solicitante: int
    ) -> Solicitacao:
        espaco = self.repositorio_espaco.buscar_por_id(dados.id_espaco)
        if not espaco:
            raise EntidadeNaoEncontradaErro("Espaço", dados.id_espaco)

        if dados.id_projeto is not None:
            projeto = self.repositorio_projeto.buscar_por_id(dados.id_projeto)
            if not projeto:
                raise EntidadeNaoEncontradaErro("Projeto", dados.id_projeto)

        usuarios_envolvidos = []
        for id_usuario in dados.ids_usuarios_envolvidos:
            if id_usuario == id_solicitante:
                raise RegraDeNegocioErro(
                    "O solicitante já está identificado e não deve ser repetido "
                    "na lista de usuários envolvidos."
                )

            usuario = self.repositorio_usuario.buscar_por_id(id_usuario)
            if not usuario:
                raise EntidadeNaoEncontradaErro("Usuário", id_usuario)
            if not usuario.ativo:
                raise RegraDeNegocioErro(
                    f"O usuário com ID {id_usuario} está inativo e não pode ser "
                    "incluído na solicitação."
                )

            usuarios_envolvidos.append(
                UsuarioEnvolvido(
                    id_usuario=id_usuario,
                    nome_completo=usuario.nome_completo,
                )
            )

        solicitacao = Solicitacao(
            tipo=dados.tipo,
            finalidade=dados.finalidade,
            urgencia=dados.urgencia,
            id_projeto=dados.id_projeto,
            id_solicitante=id_solicitante,
            id_espaco=dados.id_espaco,
            usuarios_envolvidos=usuarios_envolvidos,
            horarios=[
                HorarioSolicitacao(
                    data_reserva=horario.data_reserva,
                    hora_inicio=horario.hora_inicio,
                    hora_fim=horario.hora_fim,
                )
                for horario in dados.horarios
            ],
        )
        return self.repositorio_solicitacao.salvar(solicitacao)
