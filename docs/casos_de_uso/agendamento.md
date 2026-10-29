# Casos de uso — Solicitações e agendamentos

O módulo `app/modulos/agendamento/` recebe solicitações de uso dos espaços e
mantém a agenda oficial. Horários semanais e pausas excepcionais são
cadastrados pelo módulo `espacos`; a disponibilidade consulta essas regras
junto às reservas confirmadas.

## Solicitações

### Criar solicitação

- Somente um usuário autenticado com perfil `Servidor` pode cadastrar.
- O solicitante é obtido do token; não pode ser informado no corpo.
- Cada pedido referencia um espaço existente. O projeto é opcional; quando
  informado, precisa existir.
- O tipo deve ser `Espaço`, `Recurso` ou `Serviço`.
- A finalidade é obrigatória. A urgência é registrada como indicação e não
  garante atendimento prioritário.
- Usuários envolvidos devem existir e estar ativos; IDs duplicados e o próprio
  solicitante não são aceitos na lista.
- É obrigatório informar ao menos um horário. Cada horário contém
  `data_reserva`, `hora_inicio` e `hora_fim`; a data e o início devem ser
  futuros, e a hora final deve ser posterior à inicial.
- A nova solicitação inicia com estado `Pendente`.

### Analisar e decidir

- Somente `Administrador` e `Coordenador` podem decidir solicitações
  pendentes.
- A decisão deve ser `Aprovado` ou `Rejeitado` e incluir justificativa com ao
  menos três caracteres.
- Ao aprovar, a aplicação revalida os horários contra o funcionamento do
  espaço, pausas, reservas confirmadas e sobreposição entre horários da
  própria solicitação.
- A aprovação cria uma reserva confirmada para cada horário e salva as
  reservas, o status e a justificativa na mesma transação.
- Se qualquer horário estiver inválido ou conflitar, a solicitação permanece
  pendente e nenhuma reserva parcial é mantida.
- A rejeição registra status e justificativa sem criar reservas.

### Listar, consultar e cancelar

- `Administrador` e `Coordenador` podem consultar todas as solicitações.
- Os demais perfis autenticados consultam somente as solicitações que abriram.
- O criador ou um `Administrador` pode cancelar uma solicitação pendente.
  Coordenadores e outros usuários não podem cancelar pedidos de terceiros.
- O cancelamento preserva a solicitação e seus dados, alterando o estado para
  `Cancelada`. Solicitações que não estejam pendentes não podem ser canceladas.

### Anexos

- Somente o `Servidor` que abriu a solicitação pode enviar anexos.
- Cada chamada aceita um arquivo PDF ou DOCX de até 150 KiB (153.600 bytes).
- A API valida a extensão e a estrutura do arquivo. O objeto é enviado ao
  bucket privado do Supabase Storage; apenas os metadados e o caminho interno
  são armazenados no banco.
- O solicitante, Administrador ou Coordenador pode solicitar um link de
  download temporário, válido por 10 minutos. A API não expõe URL pública
  permanente.

## Agenda

### Consultar disponibilidade

`GET /agendamentos/disponibilidade` verifica se um período específico pode ser
reservado. Exemplo:

```text
/agendamentos/disponibilidade?id_espaco=2&data_hora_inicio=2026-11-02T14:00:00&data_hora_fim=2026-11-02T16:00:00
```

Os parâmetros são datetimes locais sem fuso horário. O início deve ser futuro e
o fim posterior ao início. A verificação considera:

1. se o espaço existe e está ativo;
2. o horário regular de funcionamento e eventuais pausas;
3. conflitos com reservas confirmadas na tabela `agenda_reserva`.

Um intervalo válido, mas indisponível, retorna `200` com `disponivel: false` e
o motivo. Espaço inexistente retorna `404`; parâmetros inválidos retornam
`422`.

### Listar reservas

`GET /agendamentos/` exige `data_hora_inicio` e `data_hora_fim`, e aceita
`id_espaco` e `id_recurso` como filtros opcionais. Retorna reservas
confirmadas que interceptam o intervalo, incluindo os IDs dos recursos
vinculados, ordenadas pelo horário de início.

### Consultar horários livres

`GET /agendamentos/horarios-disponiveis` recebe `id_espaco`, `data_inicio` e
`data_fim` (datas inclusivas) e aceita `ids_recursos` repetidos na query. Gera
períodos de uma hora, avançando em passos de uma hora a partir da abertura
cadastrada. O retorno exclui fechamentos, pausas, reservas do espaço e
conflitos de qualquer recurso informado. A consulta é limitada a 31 dias.

### Complementação e proposta de replanejamento

- `POST /solicitacoes/{id_solicitacao}/complementacao`: Administrador ou
  Coordenador registra um pedido de complementação; a solicitação aguarda a
  resposta do solicitante.
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
| `POST` | `/solicitacoes/` | Servidor |
| `GET` | `/solicitacoes/` | Usuário autenticado; resultados conforme perfil |
| `PATCH` | `/solicitacoes/{id_solicitacao}/decisao` | Administrador ou Coordenador |
| `GET` | `/solicitacoes/{id_solicitacao}` | Solicitante, Administrador ou Coordenador |
| `PATCH` | `/solicitacoes/{id_solicitacao}` | Criador ou Administrador |
| `POST` | `/solicitacoes/{id_solicitacao}/anexos` | Servidor solicitante |
| `GET` | `/solicitacoes/{id_solicitacao}/anexos/{id_anexo}/url` | Solicitante, Administrador ou Coordenador |
| `GET` | `/agendamentos/disponibilidade` | Usuário autenticado |
| `GET` | `/agendamentos/` | Usuário autenticado |
| `GET` | `/agendamentos/horarios-disponiveis` | Usuário autenticado |
| `POST` | `/solicitacoes/{id_solicitacao}/complementacao` | Administrador ou Coordenador |
| `POST` | `/solicitacoes/{id_solicitacao}/complementacao/resposta` | Servidor solicitante |
| `POST` | `/solicitacoes/{id_solicitacao}/propostas-replanejamento` | Administrador ou Coordenador |
| `POST` | `/solicitacoes/{id_solicitacao}/propostas-replanejamento/{id_interacao}/resposta` | Servidor solicitante |

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

A tabela `agenda_reserva` guarda início, fim, situação, solicitação e espaço.
Para criar as tabelas necessárias em um Supabase já existente, siga as
instruções de [migração no banco de dados](../banco_dados.md). `create_all`
cria tabelas ausentes, mas não altera as já existentes.

Turnos de monitoria permanecem para etapa futura.
