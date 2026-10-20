# Casos de uso — Usuários

Este documento descreve o comportamento implementado em `app/modulos/usuarios/`.
Os endpoints usam o prefixo `/usuarios`. Os perfis disponíveis são
`Administrador`, `Coordenador`, `Servidor`, `Monitor` e `Aluno`.

## Visão geral dos fluxos

| Caso de uso | Endpoint | Acesso |
|---|---|---|
| Cadastrar servidor | `POST /usuarios/servidor` | Público |
| Cadastrar usuário interno | `POST /usuarios/interno` | Administrador ou Coordenador |
| Autenticar | `POST /usuarios/login` | Público |
| Consultar usuário autenticado | `GET /usuarios/me` | Usuário autenticado |
| Listar usuários | `GET /usuarios/` | Administrador ou Coordenador |

Os endpoints são definidos em `interface/roteador.py`; as dependências em
`interface/dependencias.py` montam os casos de uso com repositório, codificador
de senha e, para autenticação, serviço de JWT.

## Cadastro de servidor

**Caso de uso:** `CadastrarUsuarioCasoDeUso.servidor`.

1. Recebe `CriarServidor`.
2. Verifica se CPF, e-mail ou vínculo institucional já estão cadastrados.
3. Cria usuário com perfil `Servidor` e ativo.
4. Codifica a senha antes de enviar o usuário ao repositório.
5. Retorna `UsuarioResposta` com HTTP 201.

O perfil não é fornecido pelo cliente nesse endpoint: o fluxo define
explicitamente `Servidor`.

### Entrada

- `nome_completo`: obrigatório, 3–150 caracteres.
- `cpf`: obrigatório, 11–14 caracteres.
- `vinculo_institucional`: obrigatório, mínimo de 3 caracteres.
- `email`: obrigatório e validado como endereço de e-mail.
- `senha`: obrigatório, segredo com mínimo de 8 caracteres.

CPF, e-mail e vínculo são verificados individualmente. Quando algum já está
em uso, o caso de uso lança `ConflitoDeDadosErro` (HTTP 409), indicando qual
identificador está duplicado.

## Cadastro de usuário interno

**Caso de uso:** `CadastrarUsuarioCasoDeUso.interno`.

Recebe os mesmos dados de identificação e senha do cadastro de servidor, mais
`perfil`. O endpoint requer Administrador ou Coordenador. A autorização do
perfil de destino é verificada no caso de uso:

- Administrador pode criar Administradores, Coordenadores, Servidores,
  Monitores e Alunos.
- Coordenador pode criar Servidores, Monitores e Alunos.
- Coordenador não pode criar Administradores nem outros Coordenadores.

Depois da autorização, aplica as mesmas verificações de duplicidade do fluxo
de servidor, codifica a senha, cria o usuário ativo e persiste.
Perfil de destino não permitido gera `AcessoNegadoErro` (HTTP 403); conflito
de CPF, e-mail ou vínculo gera HTTP 409.

## Autenticação

**Caso de uso:** `AutenticarUsuarioCasoDeUso.executar`.

Recebe `UsuarioLogin` (`identificacao` e `senha`). Se a identificação contiver
`@`, é tratada como e-mail; caso contrário, o fluxo remove pontos e hífens e
a trata como CPF. O repositório busca por igualdade exata. Depois, o
codificador verifica a senha e, em caso de sucesso, o serviço JWT gera token
assinado com HS256. O payload contém o ID do usuário em `sub` e os horários
de emissão (`iat`) e expiração (`exp`).

A resposta `TokenResposta` contém `access_token`, `token_type` (`bearer`) e
os dados do usuário no formato `UsuarioResposta`.

- Usuário não encontrado ou senha incorreta: `CredenciaisInvalidasErro`
  (HTTP 401).
- Senha correta para usuário inativo: `AcessoNegadoErro` (HTTP 403), com
  orientação para procurar a coordenação.
- A validade do token usa a chave secreta e a duração configuradas na
  aplicação.

## Consultar usuário autenticado

**Endpoint:** `GET /usuarios/me`.

`obter_usuario_atual` exige um token Bearer válido, decodifica o JWT, recupera
o ID em `sub`, busca novamente o usuário no banco e rejeita contas inativas.
O handler retorna `UsuarioResposta`: ID, nome, CPF, vínculo institucional,
e-mail, perfil e situação ativa. Senha e hash nunca fazem parte desse
esquema.

## Listar usuários

**Caso de uso:** `ListarUsuariosCasoDeUso.executar`.

Disponível a Administrador e Coordenador. Aceita filtros de query opcionais:

- `perfil`: um dos perfis suportados.
- `ativo`: filtra por estado ativo/inativo.
- `skip`: deslocamento, mínimo 0, padrão 0.
- `limit`: quantidade, entre 1 e 100, padrão 100.

O caso de uso encaminha filtros e paginação ao repositório e retorna uma lista
de `UsuarioResposta` (HTTP 200), sem envelope de total ou metadados. A consulta
usa `offset` e `limit`, sem ordenação explícita.

## Autenticação e autorização HTTP

As rotas protegidas usam HTTP Bearer. A dependência obtém o usuário atual antes
de verificar perfis; `VerificarPerfil` lança `AcessoNegadoErro` se o perfil
não estiver autorizado. Em condições normais, tokens inválidos ou sem `sub`
resultam em HTTP 401. As rotas públicas são cadastro de servidor e login.

## Persistência e regras relevantes

- `UsuarioModelo` guarda nome, CPF, vínculo, e-mail, hash da senha, perfil e
  estado ativo. CPF, vínculo e e-mail têm restrições de unicidade.
- O repositório copia dados para o modelo ORM, executa `commit` e `refresh`
  ao salvar.
- `ativo` inicia como verdadeiro; não há caso de uso implementado neste
  módulo para editar, desativar, reativar, excluir ou recuperar senha.
- A listagem e a resposta pessoal incluem CPF, e-mail e vínculo; o esquema
  omite o hash de senha.

## Limitações conhecidas do comportamento atual

- CPF tem validação de comprimento, mas não validação de dígitos ou
  normalização consistente. O cadastro salva o valor recebido; no login,
  pontos e hífens são removidos antes da busca. Um CPF salvo formatado pode,
  portanto, não coincidir com o valor normalizado consultado.
- A identificação do login não remove espaços; e-mail é pesquisado com
  igualdade exata.
- O esquema de vínculo exige mínimo de 3 caracteres, mas não declara o limite
  de 50 caracteres da coluna do banco.
- A verificação de unicidade é feita antes de persistir. Uma concorrência
  entre cadastros pode ainda resultar em erro de integridade do banco; não há
  conversão específica dessa falha no caso de uso.
- A dependência HTTP chama a exceção de credenciais inválidas com mensagem
  posicional para usuário inexistente/inativo, embora o construtor atual de
  `CredenciaisInvalidasErro` não aceite argumento. Esses caminhos podem
  resultar em `TypeError` em vez do HTTP pretendido.
- A conversão do `sub` do token para inteiro ocorre fora do bloco que captura
  erros de decodificação; `sub` não numérico pode propagar `ValueError`.
- O resumo da rota de listagem a descreve como pública, mas a dependência
  efetiva exige Administrador ou Coordenador.
- Há uma divergência de tipos no contrato e na implementação do repositório
  para `salvar`: o caso de uso fornece `Usuario`, enquanto a implementação
  declara `UsuarioModelo`; ela copia os atributos para construir o modelo.

