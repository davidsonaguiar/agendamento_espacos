# Casos de uso — Solicitações

O módulo permite registrar e acompanhar pedidos de uso de espaços do COLAB. A
decisão sobre a solicitação pertence a uma etapa futura do fluxo de
agendamento.

## Casos implementados

### Criar solicitação

- Somente um usuário autenticado com perfil `Servidor` pode cadastrar.
- O solicitante é obtido do token; não pode ser informado no corpo.
- Cada pedido referencia exatamente um espaço existente.
- O projeto é opcional; quando informado, precisa existir.
- O tipo deve ser `Espaço`, `Recurso` ou `Serviço`.
- A finalidade é um texto obrigatório que descreve o contexto de uso, como
  pesquisa, extensão ou atividade de disciplina.
- A urgência é registrada como indicação e não garante atendimento prioritário.
- Usuários envolvidos são referências a contas existentes e ativas. A lista
  não aceita IDs duplicados nem repetir o próprio solicitante.
- A nova solicitação inicia com estado `Pendente` e sem justificativa de
  decisão.

### Listar solicitações

- `Administrador` e `Coordenador` recebem todas as solicitações.
- Os demais perfis autenticados recebem somente as solicitações que abriram.

### Consultar uma solicitação

- `Administrador` e `Coordenador` podem consultar qualquer solicitação.
- O solicitante pode consultar as próprias.
- Outros usuários autenticados recebem `403 Forbidden`.
- IDs inexistentes retornam `404 Not Found`.

## Rotas

| Método | Rota | Acesso |
|---|---|---|
| `POST` | `/solicitacoes/` | Servidor |
| `GET` | `/solicitacoes/` | Usuário autenticado; filtragem conforme perfil |
| `GET` | `/solicitacoes/{id_solicitacao}` | Solicitante, Administrador ou Coordenador |

Exemplo de corpo para criação:

```json
{
  "tipo": "Espaço",
  "finalidade": "Pesquisa",
  "urgencia": false,
  "id_projeto": 1,
  "id_espaco": 2,
  "ids_usuarios_envolvidos": [3, 4]
}
```

`id_projeto` e `ids_usuarios_envolvidos` são opcionais. `id_espaco` é
obrigatório.

## Fora do escopo atual

Conforme os requisitos ainda a validar, esta etapa não implementa horários
desejados, validação de disponibilidade ou conflitos, recursos, anexos,
aprovação/rejeição, pedido de complementação, replanejamento ou criação de
reservas na agenda. O estado inicial é armazenado como texto para permitir
que o futuro fluxo de análise introduza seus estados sem restringir o esquema
atual.
