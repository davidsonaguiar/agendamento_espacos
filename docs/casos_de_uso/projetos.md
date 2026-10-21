# Casos de uso — Projetos

O módulo `app/modulos/projetos/` registra projetos, seus responsáveis,
criadores e participantes. O roteador usa o prefixo `/projetos`. O projeto
não tem status próprio.

## Modelo e distinções importantes

- `id_responsavel`: usuário encarregado do projeto; é definido pelo pedido
  de criação e pode ser diferente de quem cria.
- `id_criador`: usuário autenticado que cadastrou o projeto. É atribuído no
  servidor, não aceito do cliente, e dá permissão de exclusão junto com
  Administrador.
- `participantes`: associação entre projeto e usuário com papel textual.
- `quantidade_participantes`: campo informativo; não é automaticamente
  sincronizado com a quantidade de associações.

## Endpoints

| Operação | Endpoint | Autorização | Sucesso |
|---|---|---|---|
| Criar | `POST /projetos/` | Administrador, Coordenador, Servidor ou Monitor, sujeito à regra de atribuição | 201, `ProjetoResposta` |
| Listar | `GET /projetos/` | Autenticado; visibilidade por perfil | 200, lista |
| Consultar | `GET /projetos/{id_projeto}` | Autenticado; visibilidade por perfil | 200, `ProjetoResposta` |
| Atualizar | `PUT /projetos/{id_projeto}` | Autenticado; caso de uso exige responsável | 200, `ProjetoResposta` |
| Excluir | `DELETE /projetos/{id_projeto}` | Autenticado; caso de uso exige criador ou Administrador | 204, sem corpo |
| Adicionar participante | `POST /projetos/{id_projeto}/participantes` | Autenticado; responsável ou Administrador | 201, `ProjetoResposta` |
| Remover participante | `DELETE /projetos/{id_projeto}/participantes/{id_usuario}` | Autenticado; responsável ou Administrador | 200, `ProjetoResposta` |

Não há paginação, filtros ou ordenação configurável nas rotas de projeto.

## Criar projeto

**Caso de uso:** `CriarProjetoCasoDeUso.executar`.

1. Exige ID no usuário autenticado.
2. Busca `id_responsavel` no repositório de usuários; não encontrado gera 404.
3. Aplica a matriz de atribuição abaixo; uma atribuição não autorizada gera 403.
4. Cria projeto com `id_criador=usuario_logado.id` e os dados do corpo.
5. Persiste e retorna a entidade convertida para `ProjetoResposta`.

### Quem pode atribuir a quem

| Solicitante | Responsáveis permitidos |
|---|---|
| Administrador | Coordenador, Servidor ou ele próprio quando também for Administrador |
| Coordenador | Servidor ou ele próprio quando também for Coordenador |
| Servidor | Somente ele próprio, se também for Servidor |
| Monitor | Qualquer Servidor |
| Aluno | Não pode criar projetos pela rota |

Administrador não pode atribuir a outro Administrador; Coordenador não pode
atribuir a outro Coordenador; nenhum perfil pode atribuir responsabilidade a
Aluno ou Monitor.

### Entrada `CriarProjeto`

- `descricao`: obrigatória, 3–255 caracteres.
- `finalidade`: obrigatória, 3–255 caracteres.
- `id_responsavel`: obrigatório, inteiro positivo.
- `quantidade_participantes`: opcional/nula, mínimo zero.
- `documentacao_base`: opcional/nula, até 500 caracteres.

`id_criador` não está no esquema de entrada. A busca do responsável não filtra
usuários inativos.

## Listar e consultar: visibilidade

**Casos de uso:** `ListarProjetosCasoDeUso.executar` e
`ObterProjetoCasoDeUso.executar`.

- Administrador, Coordenador e Monitor podem consultar todos os projetos.
- Servidor consulta/lista projetos em que é responsável **ou** participante.
- Aluno consulta/lista apenas projetos em que participa.
- O fato de ser criador não concede, por si só, visibilidade a Servidor ou
  Aluno.
- Para consulta individual, projeto fora do escopo e ID inexistente são
  ambos reportados como entidade não encontrada (HTTP 404).

O repositório aplica os filtros no banco. Para servidor, o vínculo pode ser
responsabilidade ou associação de participante; para aluno, somente a
associação de participante.

## Atualizar projeto

**Caso de uso:** `AtualizarProjetoCasoDeUso.executar`.

Procura o projeto, retorna 404 se não existir e permite atualizar somente
quando o ID do usuário autenticado é igual a `id_responsavel`. Ser criador ou
Administrador não concede permissão de edição por si só.

`AtualizarProjeto` aceita campos opcionais:

- `descricao` e `finalidade`: 3–255 caracteres quando fornecidas; não podem
  ser explicitamente `null`.
- `quantidade_participantes`: inteiro não negativo ou `null`.
- `documentacao_base`: até 500 caracteres ou `null`.

Somente campos enviados são aplicados. Enviar `null` para quantidade ou
documentação limpa o valor; omitir o campo o preserva. O corpo vazio também é
aceito e ainda percorre atualização/persistência. O repositório atualiza
descrição, finalidade, quantidade e documentação; não troca responsável nem
criador.

## Excluir projeto

**Caso de uso:** `ExcluirProjetoCasoDeUso.executar`.

Busca o projeto para validar sua existência e autoriza a exclusão se:

- o solicitante for Administrador; ou
- `usuario_logado.id` for igual a `id_criador`.

O responsável não pode excluir apenas por ser responsável, a menos que
também seja criador ou Administrador. Se não houver autorização, retorna 403.
Após a validação, o repositório exclui o projeto; os vínculos de participantes
são removidos pela cascata da relação.

## Gerenciar participantes

**Caso de uso:** `GerenciarParticipantesCasoDeUso`.

As operações exigem que o solicitante seja responsável pelo projeto ou
Administrador. O criador não recebe autorização especial para gerenciar
participantes.

### Adicionar

Recebe `id_usuario` inteiro positivo e `papel_no_projeto` com 2–100
caracteres. Busca o projeto e o usuário; projeto ou usuário inexistente gera
404. Se o usuário já participa, gera conflito 409. Caso contrário, persiste a
associação e retorna o projeto atualizado (201).

Não há restrição de perfil para o participante nem verificação de que a conta
alvo esteja ativa. Papel é texto livre, sem enumeração de papéis permitidos.

### Remover

Busca o projeto e verifica a permissão. Exige que a associação projeto–usuário
exista; vínculo ausente gera 404. Remove a associação e retorna o projeto
atualizado (200). Não recalcula `quantidade_participantes`.

## Persistência, erros e limitações

- `ProjetoModelo` relaciona projeto a responsável e criador por chaves
  estrangeiras para `usuario.id`; `ProjetoParticipanteModelo` usa chave
  primária composta `(id_projeto, id_usuario)`.
- Busca de projeto carrega participantes e usuários relacionados. Salvar,
  atualizar, excluir e gerenciar participantes fazem commit no repositório.
- Entidade inexistente: HTTP 404; permissão negada: 403; participante
  duplicado: 409; credenciais sem ID de usuário na criação: 401.
- A busca do participante/responsável não rejeita usuários inativos.
- Verificação de duplicidade acontece antes da inserção; uma corrida
  concorrente ainda pode gerar erro de integridade do banco sem tradução
  específica.
- Não há ordenação explícita de projetos ou participantes.
- A exclusão de usuário responsável/criador não tem comportamento de cascata
  declarado nas respectivas FKs; depende das restrições do banco.

