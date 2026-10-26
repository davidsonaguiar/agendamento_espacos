# Casos de uso — Agendamentos

O módulo `app/modulos/agendamento/` controla a disponibilidade e as reservas
oficiais de espaços. O roteador usa o prefixo `/agendamentos`. Horários
semanais e pausas continuam sendo cadastrados e mantidos pelo módulo
`espacos`; o agendamento consulta essas regras para validar períodos.

## Endpoints

| Operação | Endpoint | Acesso | Sucesso |
|---|---|---|---|
| Consultar disponibilidade | `GET /agendamentos/disponibilidade` | Usuário autenticado | 200, disponibilidade e motivo |
| Listar reservas confirmadas | `GET /agendamentos/` | Usuário autenticado | 200, lista de reservas |

Não há endpoint público para criar reservas diretamente. Uma reserva oficial é
criada pelo caso de uso de decisão de solicitações quando uma solicitação é
aprovada.

## Consultar disponibilidade

Exemplo:

```text
/agendamentos/disponibilidade?id_espaco=2&data_hora_inicio=2026-11-02T14:00:00&data_hora_fim=2026-11-02T16:00:00
```

Os parâmetros de período são datetimes locais sem fuso horário. O período deve
ser futuro, ter fim posterior ao início, estar dentro do horário semanal ativo
do espaço e não cruzar uma pausa ou reserva confirmada.

Resposta disponível:

```json
{
  "id_espaco": 2,
  "data_hora_inicio": "2026-11-02T14:00:00",
  "data_hora_fim": "2026-11-02T16:00:00",
  "disponivel": true,
  "motivo": null
}
```

Se o espaço estiver desativado, fechado, fora do horário semanal ou ocupado,
a resposta continua sendo `200`, com `disponivel: false` e o motivo. Um espaço
inexistente retorna `404`; intervalo inválido retorna `422`.

## Listar reservas

`GET /agendamentos/` exige `data_hora_inicio` e `data_hora_fim`; aceita
`id_espaco` como filtro opcional. Retorna reservas confirmadas que interceptam
o período, em ordem crescente de início. Os parâmetros de consulta usam
datetimes locais sem fuso horário e o fim deve ser posterior ao início.

## Aprovar solicitações e criar reservas

`PATCH /solicitacoes/{id_solicitacao}/decisao` continua sendo a operação de
decisão, mas delega ao caso de uso `ReservarHorariosAprovadosCasoDeUso` as
regras de agenda. Ao aprovar:

1. verifica que a solicitação está pendente e contém horários;
2. bloqueia a linha do espaço durante a checagem para serializar aprovações
   concorrentes para o mesmo espaço;
3. revalida datas futuras, funcionamento semanal, pausas, conflitos com
   reservas confirmadas e sobreposição entre horários da solicitação;
4. adiciona uma reserva `Confirmada` para cada horário solicitado;
5. grava reservas e decisão na mesma transação do banco.

Se qualquer verificação falhar, a transação é revertida, a solicitação continua
pendente e não fica nenhuma reserva parcial. Rejeitar registra a decisão e não
gera reservas.

## Persistência

A tabela `agenda_reserva` implementa `AGENDA_RESERVA`, com início, fim,
situação, solicitação e espaço. A inicialização importa o modelo pelo ciclo de
vida da aplicação. Em bancos Supabase já existentes, aplique também o SQL de
migração de `agenda_reserva` descrito em [banco_dados.md](../banco_dados.md);
`create_all` não altera tabelas existentes.

`AGENDA_RESERVA_RECURSO` permanece para a etapa futura de recursos.
