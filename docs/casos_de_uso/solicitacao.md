# Casos de uso — Solicitações

O diretório `app/modulos/solicitacao/` contém arquivos estruturais vazios para
domínio, infraestrutura e interface. Na versão atual não há casos de uso,
rotas, esquemas, modelos ORM, repositório ou dependências funcionais
implementados.

## O que existe

Os arquivos atualmente presentes são:

- `dominio/contratos.py`
- `dominio/entidades.py`
- `infra/modelos.py`
- `infra/repositorios.py`
- `interface/dependencias.py`
- `interface/esquemas.py`
- `interface/roteador.py`

Eles não definem símbolos ou comportamento. Por isso, não há endpoints sob
`/solicitacao`, nem fluxo de criação, análise, aprovação, rejeição,
replanejamento ou reserva que possa ser usado pela aplicação.

## Modelo conceitual não implementado

O modelo relacional proposto em [`../banco_dados.md`](../banco_dados.md)
descreve solicitações de uso, horários pretendidos, recursos requisitados e
anexos, além de reservas resultantes de aprovação. Essa descrição é
conceitual: não constitui regra executável nem contrato de API nesta versão.

Não se deve presumir, portanto, validação de disponibilidade, conflito de
horário, autorização de recursos, controle de urgência, aprovação por
coordenador ou gravação em agenda. Esses comportamentos dependem da futura
implementação do módulo.

