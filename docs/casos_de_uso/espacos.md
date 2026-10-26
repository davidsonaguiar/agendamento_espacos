# Casos de uso — Espaços

O módulo `app/modulos/espacos/` administra espaços físicos, dados básicos,
horários semanais, pausas excepcionais e vínculos de usuários. O roteador usa
o prefixo `/espacos`.

## Endpoints e autorização

| Operação | Endpoint | Perfil exigido | Resposta de sucesso |
|---|---|---|---|
| Cadastrar | `POST /espacos/` | Administrador | 201, `EspacoResposta` |
| Listar | `GET /espacos/` | Autenticado | 200, lista de `EspacoResposta` |
| Desativar | `DELETE /espacos/{id_espaco}` | Administrador | 200, `EspacoResposta` |
| Atualizar dados | `PUT /espacos/{id_espaco}` | Administrador ou Coordenador | 200, `EspacoResposta` |
| Reativar | `PATCH /espacos/{id_espaco}/reativar` | Administrador | 200, `EspacoResposta` |
| Atualizar horário | `PATCH /espacos/{id_espaco}/horarios` | Administrador ou Coordenador | 200 |
| Consultar horários | `GET /espacos/{id_espaco}/horarios` | Autenticado | 200, lista de `HorarioFuncionamentoResposta` |
| Vincular usuário | `POST /espacos/{id_espaco}/usuarios/{id_usuario}` | Administrador ou Coordenador | 201 |
| Desvincular usuário | `DELETE /espacos/{id_espaco}/usuarios/{id_usuario}` | Administrador ou Coordenador | 200 |
| Adicionar pausa | `POST /espacos/{id_espaco}/pausas` | Administrador ou Coordenador | 201, `PausaResposta` |
| Listar pausas | `GET /espacos/{id_espaco}/pausas` | Autenticado | 200, lista de `PausaResposta` |
| Remover pausa | `DELETE /espacos/{id_espaco}/pausas/{id_pausa}` | Administrador ou Coordenador | 200 |

Os endpoints protegidos carregam o usuário autenticado e verificam perfis na
camada HTTP. Respostas de horário, vínculo e remoção de pausa não declaram
`response_model`; seus corpos vêm diretamente dos valores retornados pelo
caso de uso.

## Cadastro de espaço

**Caso de uso:** `CadastrarEspacoCasoDeUso.executar`.

Recebe `CriarEspaco`, rejeita nome já utilizado e persiste o novo espaço.
Também inicializa sete registros de horário, um por dia da semana, com
abertura às 08:00 e fechamento às 18:00: segunda a sexta ativos e sábado e
domingo inativos. O repositório salva espaço e horários na transação de
cadastro. Retorna `EspacoResposta` com HTTP 201.

Campos de entrada:

- `nome`: obrigatório, mínimo de 3 caracteres.
- `descricao`, `capacidade` e `bloco`: opcionais.
- `disponibilidade`: opcional, padrão verdadeiro.

O esquema não impõe limite máximo de texto nem capacidade positiva. O modelo
do banco limita nome a 100 caracteres, descrição a 255 e bloco a 50; capacidade
é inteiro. Nome duplicado gera conflito (HTTP 409).

## Listar espaços

**Caso de uso:** `ListarEspacosCasoDeUso.executar`.

Aceita `skip` (mínimo 0, padrão 0) e `limit` (1–100, padrão 100). A saída é
uma lista simples, sem total:

- Administrador: todos os espaços, ativos ou desativados.
- Servidor: somente espaços disponíveis/ativos.
- Coordenador ou Monitor: somente espaços vinculados ao usuário.
- Outros perfis autenticados: lista vazia.

O repositório aplica os filtros e limites, sem ordenar explicitamente os
resultados.

## Atualizar dados de espaço

**Caso de uso:** `AtualizarEspacoCasoDeUso.executar`.

Recebe `AtualizarEspaco`, cujos campos são opcionais: nome (mínimo 3 quando
informado), descrição, capacidade e bloco. Procura o espaço, rejeita se ele
não existir e verifica se outro espaço já utiliza o novo nome. Atualiza os
valores informados que não sejam `None`.

`disponibilidade` não pode ser alterada por esta operação: use as rotas de
desativar e reativar. Valores `null` são ignorados, portanto este `PUT` não
serve para limpar descrição, capacidade ou bloco.

## Desativar e reativar

- **`DesativarEspacoCasoDeUso`** define `disponibilidade=False`; é uma
  desativação lógica, não remove o registro. Espaço inexistente gera 404.
- **`ReativarEspacoCasoDeUso`** define `disponibilidade=True`. Espaço
  inexistente gera 404; tentar reativar um espaço já ativo gera conflito
  (409).

Ambas as ações são restritas a Administrador.

## Horário semanal

**Caso de uso:** `AtualizarHorariosEspacoCasoDeUso.executar`.

Recebe `AtualizarHorario` com `dia_semana` de 0 a 6 (0=domingo, 1=segunda,
…, 6=sábado), `hora_abertura`, `hora_fechamento` e `ativo`. O caso de uso
verifica se o espaço existe e constrói a entidade de horário; o domínio exige
que fechamento seja posterior à abertura. Depois, o repositório procura o
registro existente para aquele espaço e dia e atualiza suas horas e estado.

`GET /espacos/{id_espaco}/horarios` verifica se o espaço existe e retorna os
horários ordenados por `dia_semana`, incluindo `ativo`, abertura e fechamento.
Um espaço inexistente retorna 404; a rota requer autenticação, mas está
disponível para qualquer perfil autenticado. Atualização de um dia sem
registro prévio levanta `ValueError` em vez de criar um novo registro.

O cálculo da disponibilidade e a consulta de reservas estão no módulo
`agendamento`; a verificação do funcionamento semanal e das pausas usa as
regras e os dados mantidos pelo módulo de espaços. Veja
[casos de uso de agendamentos](./agendamento.md).

## Gerenciar vínculos de usuários

**Caso de uso:** `GerenciarVinculosCasoDeUso`.

- Vincular: verifica existência do espaço e do usuário, valida perfil-alvo,
  rejeita associação duplicada e associa usuário e espaço.
- Desvincular: verifica existência do espaço e do usuário, exige associação
  existente e a remove.
- Os perfis aceitos como alvo no caso de uso são Administrador, Coordenador
  e Monitor.
- As respostas de sucesso são dicionários com uma mensagem descritiva.

O handler exige Administrador ou Coordenador como solicitante. O caso de uso
não recebe a identidade do solicitante e não limita quais espaços um
Coordenador pode administrar. A mensagem de erro sobre perfis-alvo menciona
Coordenador ou Monitor, mas a regra implementada também aceita Administrador.

## Gerenciar pausas

**Caso de uso:** `GerenciarPausasEspacoCasoDeUso`.

- **Adicionar:** exige espaço existente e `CriarPausaFuncionamento`. A data
  inicial e final são obrigatórias; motivo tem mínimo de 3 caracteres. O
  domínio rejeita data final anterior à inicial. Sucesso retorna
  `PausaResposta` (201).
- **Listar:** exige espaço existente e retorna a lista de pausas (200), sem
  ordenação explícita.
- **Remover:** a rota exige espaço e pausa e retorna mensagem de sucesso
  (200).

O repositório remove a pausa pelo ID da pausa sem conferir que ela pertence ao
ID do espaço da rota. Além disso, a camada de caso de uso captura `ValueError`,
mas o repositório usa `EntidadeNaoEncontradaErro` para pausa inexistente; as
exceções esperadas não são traduzidas uniformemente.

## Esquemas de saída

- `EspacoResposta`: ID, nome, descrição, capacidade, bloco e disponibilidade.
- `PausaResposta`: ID, datas, motivo e ID do espaço.
- Ambos aceitam instâncias ORM via `from_attributes=True`.

## Limitações e comportamentos que não estão implementados

- Não há exclusão definitiva de espaço nem validação de conflito entre pausas.
- Não há limite positivo para capacidade, normalização de nomes ou validação
  dos comprimentos de textos contra todas as colunas do banco.
- Nenhuma ordenação é explicitamente solicitada para espaços ou pausas.
- A pausa não é validada contra horário de funcionamento; sua finalidade é
  apenas registrar um período de fechamento.
- Uma exceção de validação de data é `RegraDeNegocioErro`, enquanto o caso de
  uso captura `ValueError`; não se deve presumir que essa validação resulte
  na resposta HTTP especificamente pretendida sem verificar a hierarquia de
  erros compartilhada.
