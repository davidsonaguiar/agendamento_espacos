# Casos de uso — Solicitações

O módulo permite registrar e acompanhar pedidos de uso de espaços do COLAB.
A decisão da solicitação é responsabilidade deste módulo; validação de
disponibilidade e criação de reservas oficiais são delegadas ao módulo
`agendamento`.

## Casos implementados

### Analisar e decidir solicitação

- Somente `Administrador` e `Coordenador` podem decidir.
- Apenas solicitações `Pendente` podem receber decisão; decisões posteriores
  não são permitidas.
- A decisão deve ser `Aprovado` ou `Rejeitado` e deve incluir justificativa
  com ao menos três caracteres.
- Para aprovar, o caso de uso delega ao módulo `agendamento` a verificação dos
  horários contra o funcionamento do espaço, pausas, conflitos e os demais
  horários da própria solicitação.
- A aprovação cria uma reserva confirmada para cada horário e atualiza o
  status e a justificativa na mesma transação de banco.
- Se qualquer horário conflitar ou estiver fora do funcionamento, a
  solicitação permanece pendente e nenhuma reserva é criada.
- A rejeição registra status e justificativa sem criar reservas.
- As reservas podem ser consultadas pela API de [agendamentos](./agendamento.md).

### Criar solicitação

- Somente um usuário autenticado com perfil `Servidor` pode cadastrar.
- O solicitante é obtido do token; não pode ser informado no corpo.
- Cada pedido referencia exatamente um espaço existente.
- O projeto é opcional; quando informado, precisa existir.
- O tipo deve ser `Espaço`, `Recurso` ou `Serviço`.
- A finalidade é obrigatória.
- A urgência é registrada como indicação e não garante atendimento prioritário.
- Usuários envolvidos são referências a contas existentes e ativas. A lista
  não aceita IDs duplicados nem repetir o próprio solicitante.
- É obrigatório informar pelo menos um horário. Cada horário contém
  `data_reserva`, `hora_inicio` e `hora_fim`; a data e o início devem ser
  futuros, e a hora final deve ser posterior à inicial.
- A nova solicitação inicia com estado `Pendente` e sem justificativa de
  decisão.

### Listar e consultar solicitações

- `Administrador` e `Coordenador` recebem e podem consultar todas as
  solicitações.
- Os demais perfis autenticados recebem somente as solicitações que abriram.
- Outros usuários autenticados recebem `403 Forbidden` ao consultar uma
  solicitação alheia.

### Adicionar anexo

- Somente o `Servidor` que abriu a solicitação pode enviar anexos.
- Cada chamada aceita um arquivo PDF ou DOCX com até 150 KiB (153.600 bytes).
- A API verifica a extensão e a assinatura/estrutura do conteúdo do arquivo.
- O objeto é enviado ao bucket privado do Supabase Storage; somente os
  metadados e o caminho interno do objeto são armazenados no banco.
- O bucket precisa se chamar `anexos-solicitacoes` (ou corresponder a
  `SUPABASE_BUCKET_ANEXOS`) e ser configurado como privado.
- A listagem e a consulta da solicitação retornam nome, tipo e data do anexo,
  sem expor seu caminho privado.

### Baixar anexo

- O solicitante, Administrador ou Coordenador pode solicitar um link de
  download temporário.
- O link assinado expira após 10 minutos.
- A API não disponibiliza uma URL pública permanente.

## Rotas

| Método | Rota | Acesso |
|---|---|---|
| `POST` | `/solicitacoes/` | Servidor |
| `GET` | `/solicitacoes/` | Usuário autenticado; filtragem conforme perfil |
| `PATCH` | `/solicitacoes/{id_solicitacao}/decisao` | Administrador ou Coordenador |
| `GET` | `/solicitacoes/{id_solicitacao}` | Solicitante, Administrador ou Coordenador |
| `POST` | `/solicitacoes/{id_solicitacao}/anexos` | Servidor solicitante |
| `GET` | `/solicitacoes/{id_solicitacao}/anexos/{id_anexo}/url` | Solicitante, Administrador ou Coordenador |

Exemplo de corpo para criação:

```json
{
  "tipo": "Espaço",
  "finalidade": "Pesquisa",
  "urgencia": false,
  "id_projeto": 1,
  "id_espaco": 2,
  "ids_usuarios_envolvidos": [3, 4],
  "horarios": [
    {
      "data_reserva": "2099-10-20",
      "hora_inicio": "14:00:00",
      "hora_fim": "16:00:00"
    },
    {
      "data_reserva": "2099-10-22",
      "hora_inicio": "14:00:00",
      "hora_fim": "16:00:00"
    }
  ]
}
```

`id_projeto` e `ids_usuarios_envolvidos` são opcionais. `id_espaco` e a lista
`horarios` são obrigatórios.

Exemplo de corpo para aprovar ou rejeitar:

```json
{
  "status": "Aprovado",
  "justificativa": "Horários verificados e aprovados."
}
```

O upload é `multipart/form-data`, no campo `arquivo`. A resposta de
`POST /solicitacoes/{id_solicitacao}/anexos` contém os metadados do anexo.
Para obter o download, consulte a rota terminada em `/url`; a resposta contém
`url_assinada` e `validade_segundos`.

## Configuração do Supabase Storage

1. Crie um bucket privado chamado `anexos-solicitacoes` no projeto Supabase.
2. Configure o limite do bucket para 153.600 bytes e permita os tipos
   `application/pdf` e
   `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
3. Configure no ambiente do servidor:

   ```env
   SUPABASE_URL=https://<seu-projeto>.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=<chave-service-role>
   SUPABASE_BUCKET_ANEXOS=anexos-solicitacoes
   ```

   A chave `service_role` deve permanecer somente no ambiente seguro do
   backend. Não a use no frontend nem a envie em mensagens.

## Fora do escopo atual

Esta etapa não implementa recursos, pedido de complementação ou
replanejamento. A decisão cria reservas na agenda apenas ao aprovar uma
solicitação.
