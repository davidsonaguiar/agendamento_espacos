from app.compartilhado.dominio.erros import EntidadeNaoEncontradaErro
from app.modulos.espacos.dominio.contratos import (
    EspacoRepositorioContrato,
    RegrasHorarioRepositorioContrato,
)
from app.modulos.espacos.dominio.entidades import EspacoPausaFuncionamento
from app.modulos.espacos.interface.esquemas import CriarPausaFuncionamento


class GerenciarPausasEspacoCasoDeUso:
    def __init__(
        self, 
        repo_espaco: EspacoRepositorioContrato, 
        repo_horario: RegrasHorarioRepositorioContrato
    ):
        self.repo_espaco = repo_espaco
        self.repo_horario = repo_horario

    def _validar_espaco(self, id_espaco: int):
        if not self.repo_espaco.buscar_por_id(id_espaco):
            raise EntidadeNaoEncontradaErro(entidade="Espaço", id=id_espaco)

    def listar(self, id_espaco: int) -> list[EspacoPausaFuncionamento]:
        self._validar_espaco(id_espaco)
        return self.repo_horario.buscar_pausas_por_espaco(id_espaco)

    def adicionar(self, id_espaco: int, dados: CriarPausaFuncionamento) -> EspacoPausaFuncionamento:
        self._validar_espaco(id_espaco)

        try:
            nova_pausa = EspacoPausaFuncionamento(
                data_inicio=dados.data_inicio,
                data_fim=dados.data_fim,
                motivo=dados.motivo,
                id_espaco=id_espaco
            )
        except ValueError as e:
            raise EntidadeNaoEncontradaErro(entidade="Pausa de Funcionamento", id=id_espaco, detalhe=str(e))

        return self.repo_horario.adicionar_pausa(nova_pausa)

    def remover(self, id_espaco: int, id_pausa: int) -> dict:
        self._validar_espaco(id_espaco)
        self.repo_horario.remover_pausa(id_pausa)
        return {"mensagem": "Pausa removida com sucesso."}
        