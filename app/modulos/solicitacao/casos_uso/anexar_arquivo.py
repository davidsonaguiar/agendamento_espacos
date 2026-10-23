import logging
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

from app.compartilhado.dominio.erros import (
    AcessoNegadoErro,
    CredenciaisInvalidasErro,
    EntidadeNaoEncontradaErro,
    FalhaPersistenciaErro,
    RegraDeNegocioErro,
    TamanhoArquivoExcedidoErro,
)
from app.modulos.solicitacao.dominio.contratos import (
    ArmazenamentoAnexoContrato,
    SolicitacaoRepositorioContrato,
)
from app.modulos.solicitacao.dominio.entidades import AnexoSolicitacao

logger = logging.getLogger(__name__)
LIMITE_ANEXO_BYTES = 150 * 1024


class AnexarArquivoSolicitacaoCasoDeUso:
    def __init__(
        self,
        repositorio: SolicitacaoRepositorioContrato,
        armazenamento: ArmazenamentoAnexoContrato,
    ):
        self.repositorio = repositorio
        self.armazenamento = armazenamento

    def executar(
        self,
        id_solicitacao: int,
        id_solicitante: int | None,
        nome_arquivo: str | None,
        conteudo: bytes,
    ) -> AnexoSolicitacao:
        if id_solicitante is None:
            raise CredenciaisInvalidasErro()

        solicitacao = self.repositorio.buscar_por_id(id_solicitacao)
        if solicitacao is None:
            raise EntidadeNaoEncontradaErro("Solicitação", id_solicitacao)
        if solicitacao.id_solicitante != id_solicitante:
            raise AcessoNegadoErro(
                "Somente o solicitante pode adicionar anexos."
            )

        nome_seguro, tipo_conteudo = self._validar_arquivo(nome_arquivo, conteudo)
        caminho = f"{id_solicitacao}/{uuid4().hex}_{nome_seguro}"
        self.armazenamento.enviar(caminho, conteudo, tipo_conteudo)

        try:
            return self.repositorio.salvar_anexo(
                id_solicitacao=id_solicitacao,
                nome_arquivo=nome_seguro,
                url_caminho=caminho,
                tipo_arquivo=tipo_conteudo,
                data_upload=datetime.now(timezone.utc),
            )
        except FalhaPersistenciaErro:
            logger.exception(
                "Não foi possível salvar os metadados do anexo da solicitação %s.",
                id_solicitacao,
            )
            self.armazenamento.remover(caminho)
            raise

    @staticmethod
    def _validar_arquivo(
        nome_arquivo: str | None, conteudo: bytes
    ) -> tuple[str, str]:
        if not nome_arquivo:
            raise RegraDeNegocioErro("Informe um nome de arquivo.")
        if not conteudo:
            raise RegraDeNegocioErro("O arquivo enviado está vazio.")
        if len(conteudo) > LIMITE_ANEXO_BYTES:
            raise TamanhoArquivoExcedidoErro(LIMITE_ANEXO_BYTES)

        nome_original = nome_arquivo.replace("\\", "/").split("/")[-1]
        extensao = nome_original.rpartition(".")[2].lower()
        nome_seguro = re.sub(r"[^A-Za-z0-9._-]", "_", nome_original)[:255]
        if extensao == "pdf":
            if not conteudo.startswith(b"%PDF-"):
                raise RegraDeNegocioErro("O conteúdo do arquivo não é um PDF válido.")
            tipo_conteudo = "application/pdf"
        elif extensao == "docx":
            try:
                with zipfile.ZipFile(BytesIO(conteudo)) as documento:
                    nomes = set(documento.namelist())
            except (OSError, zipfile.BadZipFile) as erro:
                raise RegraDeNegocioErro(
                    "O conteúdo do arquivo não é um DOCX válido."
                ) from erro
            if (
                "[Content_Types].xml" not in nomes
                or "word/document.xml" not in nomes
            ):
                raise RegraDeNegocioErro(
                    "O conteúdo do arquivo não é um DOCX válido."
                )
            tipo_conteudo = (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        else:
            raise RegraDeNegocioErro("Somente arquivos PDF e DOCX são permitidos.")

        if not nome_seguro or nome_seguro.startswith("."):
            raise RegraDeNegocioErro("Informe um nome de arquivo válido.")
        return nome_seguro, tipo_conteudo
