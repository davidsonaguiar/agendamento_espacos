from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import (
    EspacoRepositorioContrato,
    RecursoRepositorioContrato,
)
from app.modulos.espacos.dominio.entidades import Recurso
from app.modulos.espacos.interface.esquemas import AtualizarRecurso, CriarRecurso
from app.modulos.usuarios.dominio.entidades import PerfilUsuario, Usuario


class GerenciarRecursosEspacoCasoDeUso:
    def __init__(
        self,
        repo_espaco: EspacoRepositorioContrato,
        repo_recurso: RecursoRepositorioContrato,
    ):
        self.repo_espaco = repo_espaco
        self.repo_recurso = repo_recurso

    def listar(
        self,
        id_espaco: int,
        usuario_logado: Usuario,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Recurso]:
        self._validar_espaco(id_espaco)
        pode_ver_indisponiveis = usuario_logado.perfil in {
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.COORDENADOR,
            PerfilUsuario.MONITOR,
        }
        return self.repo_recurso.listar_por_espaco(
            id_espaco,
            apenas_disponiveis=not pode_ver_indisponiveis,
            skip=skip,
            limit=limit,
        )

    def adicionar(self, id_espaco: int, dados: CriarRecurso) -> Recurso:
        self._validar_espaco(id_espaco)
        recurso = Recurso(
            nome=dados.nome,
            tipo=dados.tipo,
            autorizacao_necessaria=dados.autorizacao_necessaria,
            reserva_independente=dados.reserva_independente,
            id_espaco=id_espaco,
        )
        return self.repo_recurso.salvar(recurso)

    def atualizar(
        self,
        id_espaco: int,
        id_recurso: int,
        dados: AtualizarRecurso,
    ) -> Recurso:
        self._validar_espaco(id_espaco)
        recurso = self._buscar_recurso_do_espaco(id_espaco, id_recurso)

        for campo in dados.model_fields_set:
            setattr(recurso, campo, getattr(dados, campo))

        return self.repo_recurso.atualizar(recurso)

    def indisponibilizar(self, id_espaco: int, id_recurso: int) -> Recurso:
        self._validar_espaco(id_espaco)
        recurso = self._buscar_recurso_do_espaco(id_espaco, id_recurso)

        self.repo_recurso.excluir(id_recurso)
        recurso.disponibilidade = False
        return recurso

    def _validar_espaco(self, id_espaco: int) -> None:
        if self.repo_espaco.buscar_por_id(id_espaco) is None:
            raise EntidadeNaoEncontradaErro("Espaço", id_espaco)

    def _buscar_recurso_do_espaco(self, id_espaco: int, id_recurso: int) -> Recurso:
        recurso = self.repo_recurso.buscar_por_id(id_recurso)
        if recurso is None or recurso.id_espaco != id_espaco:
            raise EntidadeNaoEncontradaErro("Recurso", id_recurso)
        return recurso
