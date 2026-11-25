# Casos de uso — Solicitações e agendamentos

O módulo `app/modulos/agendamento/` recebe solicitações de uso dos espaços e
mantém a agenda oficial. Horários semanais e pausas excepcionais são
cadastrados pelo módulo `espacos`; a disponibilidade consulta essas regras
junto às reservas confirmadas.

## Solicitações

### Criar solicitação

- Qualquer usuário autenticado com perfil global `Membro` pode cadastrar.
- O solicitante é obtido do token; não pode ser informado no corpo.
- O usuário pode reservar um espaço, adicionar recursos desse espaço à reserva,
  ou reservar somente um ou mais recursos com reserva independente habilitada.
- Ao reservar somente recursos, todos devem pertencer ao mesmo espaço físico e
  ser marcados como `reserva_independente`. Esse espaço físico fornece as regras
  de funcionamento, mas não é bloqueado pela reserva.
- Quando um espaço é selecionado, os recursos informados devem pertencer a ele;
  nesse caso o espaço inteiro é reservado, com ou sem recursos associados.
- O projeto é opcional; quando informado, precisa existir.
- A finalidade é obrigatória. A urgência é registrada como indicação e não
  garante atendimento prioritário.
- Usuários envolvidos devem existir e estar ativos; IDs duplicados e o próprio
  solicitante não são aceitos na lista.
- É obrigatório informar ao menos um horário. Cada horário contém
  `data_reserva`, `hora_inicio` e `hora_fim`; a data e o início devem ser
  futuros, e a hora final deve ser posterior à inicial.
- A nova solicitação inicia com estado `Pendente`.
- O campo `id_espaco` pode ser omitido somente quando `ids_recursos` contém ao
  menos um recurso elegível para reserva independente. O tipo da solicitação não
  define o alvo do agendamento.

### Analisar e decidir

- `Administrador` pode decidir solicitações de qualquer espaço. Um
  `Coordenador` pode decidir solicitações somente dos espaços em que está
  vinculado como Coordenador. O perfil `Monitor` não concede permissão para
  decidir solicitações.
- A decisão deve ser `Aprovado` ou `Rejeitado` e incluir justificativa com ao
  menos três caracteres.
- Ao aprovar, a aplicação revalida os horários contra o funcionamento do
  espaço físico, pausas, reservas confirmadas e sobreposição entre horários da
  própria solicitação.
- Reservas do espaço bloqueiam qualquer reserva de recurso em seu interior.
  Reservas independentes de recursos distintos podem coincidir, mas conflitam
  com a reserva integral do espaço ou com outra reserva do mesmo recurso.
- A aprovação cria uma reserva confirmada para cada horário e salva as
  reservas, o status e a justificativa na mesma transação.
- Se qualquer horário estiver inválido ou conflitar, a solicitação permanece
  pendente e nenhuma reserva parcial é mantida.
- A rejeição registra status e justificativa sem criar reservas.

### Listar, consultar e cancelar

- `Administrador` pode consultar todas as solicitações. Um `Coordenador` pode
  consultar as solicitações dos espaços em que atua como Coordenador.
- Os demais Membros autenticados consultam somente as solicitações que
  abriram.
- O criador ou um `Administrador` pode cancelar uma solicitação pendente.
  Coordenadores e outros usuários não podem cancelar pedidos de terceiros.
- O cancelamento preserva a solicitação e seus dados, alterando o estado para
  `Cancelada`. Solicitações que não estejam pendentes não podem ser canceladas.

### Anexos

- Somente o `Membro` que abriu a solicitação pode enviar anexos.
- Cada chamada aceita um arquivo PDF ou DOCX de até 150 KiB (153.600 bytes).
- A API valida a extensão e a estrutura do arquivo. O objeto é enviado ao
  bucket privado do Supabase Storage; apenas os metadados e o caminho interno
  são armazenados no banco.
- O solicitante, um Administrador ou um Coordenador do espaço da solicitação
  pode solicitar um link de download temporário, válido por 10 minutos. A API
  não expõe URL pública permanente.

## Agenda

### Consultar disponibilidade

`GET /agendamentos/disponibilidade` verifica se um período específico pode ser
reservado. Informe `id_espaco` para consultar a reserva do espaço, ou omita-o e
informe `ids_recursos` para consultar recursos independentes. Exemplo:

```text
/agendamentos/disponibilidade?id_espaco=2&data_hora_inicio=2026-11-02T14:00:00&data_hora_fim=2026-11-02T16:00:00
```

Os parâmetros são datetimes locais sem fuso horário. O início deve ser futuro e
o fim posterior ao início. Para recursos independentes, o funcionamento do
espaço onde estão localizados continua sendo respeitado. A verificação considera:

1. se o espaço existe e está ativo;
2. o horário regular de funcionamento e eventuais pausas;
3. conflitos com reservas confirmadas na tabela `agenda_reserva`, segundo o
   alvo consultado (espaço inteiro ou recursos selecionados).

Um intervalo válido, mas indisponível, retorna `200` com `disponivel: false` e
o motivo. Espaço inexistente retorna `404`; parâmetros inválidos retornam
`422`.

### Listar reservas

`GET /agendamentos/` exige `data_hora_inicio` e `data_hora_fim`, e aceita
`id_espaco` e `id_recurso` como filtros opcionais. Retorna reservas
confirmadas que interceptam o intervalo, incluindo os IDs dos recursos
vinculados, ordenadas pelo horário de início.

### Consultar horários livres

`GET /agendamentos/horarios-disponiveis` recebe `data_inicio` e `data_fim`
(datas inclusivas). Informe `id_espaco` para horários do espaço inteiro ou
`ids_recursos` repetidos para horários de recursos independentes. Gera
períodos de uma hora, avançando em passos de uma hora a partir da abertura
cadastrada no espaço físico. O retorno respeita fechamentos, pausas, reservas do
espaço e conflitos dos recursos selecionados. A consulta é limitada a 31 dias.

### Complementação e proposta de replanejamento

- `POST /solicitacoes/{id_solicitacao}/complementacao`: Administrador ou
  Coordenador do espaço da solicitação registra um pedido de complementação;
  a solicitação aguarda a resposta do solicitante.
- `POST /solicitacoes/{id_solicitacao}/complementacao/resposta`: o solicitante
  responde e a solicitação retorna a `Pendente`.
- `POST /solicitacoes/{id_solicitacao}/propostas-replanejamento`: o gestor
  envia horários de uma hora e recursos alternativos. Os períodos são
  validados contra funcionamento, pausas e conflitos antes da proposta ser
  registrada.
- `POST /solicitacoes/{id_solicitacao}/propostas-replanejamento/{id_interacao}/resposta`:
  o solicitante pode recusar, retornando a solicitação a `Pendente`, ou aceitar.
  A aceitação atualiza horários/recursos, aprova a solicitação e cria as
  reservas na mesma transação.
- Cada ação acrescenta uma interação ao histórico da solicitação.

Não há endpoint para criar reservas diretamente. Elas são criadas somente
quando uma solicitação é aprovada.

## Rotas

| Método | Rota | Acesso |
|---|---|---|
| `POST` | `/solicitacoes/` | Membro |
| `GET` | `/solicitacoes/` | Usuário autenticado; resultados conforme perfil e espaços coordenados |
| `PATCH` | `/solicitacoes/{id_solicitacao}/decisao` | Administrador ou Coordenador do espaço |
| `GET` | `/solicitacoes/{id_solicitacao}` | Solicitante, Administrador ou Coordenador do espaço |
| `PATCH` | `/solicitacoes/{id_solicitacao}` | Criador ou Administrador |
| `POST` | `/solicitacoes/{id_solicitacao}/anexos` | Membro solicitante |
| `GET` | `/solicitacoes/{id_solicitacao}/anexos/{id_anexo}/url` | Solicitante, Administrador ou Coordenador do espaço |
| `GET` | `/agendamentos/disponibilidade` | Usuário autenticado |
| `GET` | `/agendamentos/` | Usuário autenticado |
| `GET` | `/agendamentos/horarios-disponiveis` | Usuário autenticado |
| `POST` | `/solicitacoes/{id_solicitacao}/complementacao` | Administrador ou Coordenador do espaço |
| `POST` | `/solicitacoes/{id_solicitacao}/complementacao/resposta` | Membro solicitante |
| `POST` | `/solicitacoes/{id_solicitacao}/propostas-replanejamento` | Administrador ou Coordenador do espaço |
| `POST` | `/solicitacoes/{id_solicitacao}/propostas-replanejamento/{id_interacao}/resposta` | Membro solicitante |

Exemplo de corpo para decidir uma solicitação:

```json
{
  "status": "Aprovado",
  "justificativa": "Horários verificados e aprovados."
}
```

## Supabase Storage e migração

Crie um bucket privado chamado `anexos-solicitacoes` (ou configure
`SUPABASE_BUCKET_ANEXOS`) e permita PDF e DOCX, com limite de 153.600 bytes.
Configure `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` e
`SUPABASE_BUCKET_ANEXOS` apenas no ambiente seguro do backend. A chave
`service_role` não deve ser exposta no frontend.

A tabela `agenda_reserva` guarda início, fim, situação, solicitação, espaço
físico, se o espaço inteiro está reservado, e os recursos selecionados.
Para criar as tabelas necessárias em um Supabase já existente, siga as
instruções de [migração no banco de dados](../banco_dados.md). `create_all`
cria tabelas ausentes, mas não altera as já existentes.

Turnos de monitoria permanecem para etapa futura.
