\# 🧪 Sistema de Gestão e Agendamento do COLAB (IFAL)

> API backend para gestão operacional, acadêmica e agendamento de espaços e recursos do Laboratório COLAB do Instituto Federal de Alagoas (IFAL) - Campus Maceió.

## 📖 Sobre o Projeto

Este projeto integra a disciplina de Projeto Integrador do Bacharelado em Sistemas de Informação. O sistema visa digitalizar e organizar os processos administrativos do laboratório COLAB, substituindo controles informais por uma plataforma centralizada de solicitações de uso, validação de demandas (fila de análise por coordenadores), gestão de agenda com prevenção de conflitos e histórico de utilização.

## 🚀 Tecnologias e Stack

O backend da aplicação foi construído visando alta performance, tipagem estática e padronização, utilizando o ecossistema moderno do Python:

- **Linguagem:** Python
- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) (Alta performance e documentação automática)
- **Validação de Dados:** Pydantic
- **ORM:** SQLAlchemy
- **Banco de Dados:** PostgreSQL
- **Autenticação:** JWT (JSON Web Tokens)
- **Infraestrutura:** Docker & Docker Compose

---

## 🏛️ Arquitetura Limpa e Princípios SOLID

O projeto está organizado com referências à **Arquitetura Limpa (Clean Architecture)** e aos princípios **SOLID**. A separação descrita abaixo é uma diretriz arquitetural, mas a implementação ainda não a segue integralmente: por exemplo, alguns casos de uso recebem esquemas da camada HTTP.

Todos os desenvolvedores da equipe devem seguir estas diretrizes obrigatórias ao criar ou modificar módulos:

### 1. Separação de Preocupações (Camadas)
O sistema é dividido em módulos isolados, e cada módulo possui 4 camadas restritas:
*   **Domínio (`dominio/`):** É o coração do software. Contém as entidades puras, as exceções de negócio e os **Contratos** (Interfaces Abstratas). **Regra de Ouro:** Esta camada *nunca* deve importar ferramentas externas (nada de FastAPI, SQLAlchemy ou bibliotecas de terceiros).
*   **Casos de Uso (`casos_uso/`):** Orquestra o fluxo da aplicação (ex: `CadastrarServidorCasoDeUso`). Só pode importar arquivos do Domínio.
*   **Infraestrutura (`infra/`):** Onde o sistema se conecta com o mundo externo. Aqui ficam os Modelos ORM, a conexão com o PostgreSQL, criptografia e integrações. Essas classes *implementam* os Contratos definidos no Domínio.
*   **Interface (`interface/`):** A porta de entrada da aplicação. Lida exclusivamente com HTTP, validação de JSONs de entrada/saída (Schemas Pydantic) e injeção de dependências.

### 2. Princípios SOLID Aplicados
*   **SRP (Responsabilidade Única):** Cada arquivo tem apenas um papel. O Roteador (`roteador.py`) não salva no banco; o Repositório (`repositorios.py`) não valida JSON.
*   **DIP (Inversão de Dependência):** Nossos Casos de Uso **nunca** dependem de implementações concretas (ex: `UsuarioRepositorio`). Eles dependem exclusivamente de abstrações (ex: `UsuarioRepositorioContrato`). A injeção da dependência real (Factory) é feita pela camada de Interface no arquivo `dependencias.py`. Isso permite que qualquer tecnologia (como o banco de dados) seja trocada no futuro sem alterar uma única linha das regras de negócio.

### Estrutura de Diretórios Atual
```text
app/
├── compartilhado/
│   ├── dominio/                         # Entidade base e erros compartilhados
│   └── infra/
│       └── seguranca/
└── modulos/
    ├── espacos/                           # Espaços, horários, pausas e vínculos
    │   ├── casos_uso/
    │   ├── dominio/
    │   ├── infra/
    │   └── interface/
    ├── projetos/                          # Projetos e participantes
    │   ├── casos_uso/
    │   ├── dominio/
    │   ├── infra/
    │   └── interface/
    ├── solicitacao/                       # Estrutura reservada para solicitações
    └── usuarios/                          # Cadastro, autenticação e consulta
        ├── casos_uso/
        ├── dominio/
        ├── infra/
        └── interface/

main.py                                  # Ponto de entrada da aplicação
requirements.txt
docs/
├── banco_dados.md
└── casos_de_uso/
    ├── espacos.md
    ├── projetos.md
    ├── solicitacao.md
    └── usuarios.md
```

## ⚙️ Funcionalidades

### Implementado

* Cadastro, autenticação por CPF ou e-mail, consulta do usuário autenticado e listagem administrativa de usuários. Os perfis são Administrador, Coordenador, Servidor, Monitor e Aluno.
* Cadastro e manutenção de espaços, horários de funcionamento, pausas e vínculos entre espaços e usuários.
* Cadastro, consulta e atualização de projetos, além do gerenciamento de participantes. Projetos registram separadamente o responsável e o usuário criador.
* A listagem e a consulta individual de projetos são filtradas por vínculo para Servidores e Alunos. Coordenadores, Administradores e Monitores podem consultar todos os projetos.
* A exclusão de projetos é permitida ao criador do projeto ou a um Administrador.
* Endpoint de verificação da API em `GET /`.

Os casos de uso, as regras de negócio, as restrições e os fluxos estão detalhados por módulo:

* [Usuários](docs/casos_de_uso/usuarios.md)
* [Espaços](docs/casos_de_uso/espacos.md)
* [Projetos](docs/casos_de_uso/projetos.md)
* [Solicitações (módulo ainda sem implementação)](docs/casos_de_uso/solicitacao.md)

A documentação interativa da API é gerada pelo FastAPI em `/docs` (Swagger UI) e `/redoc`.

### Ainda não implementado

O módulo `solicitacao` existe apenas como estrutura de diretórios, sem casos de uso ou rotas implementados. Recursos, solicitações de agendamento, anexos, agenda de reservas e turnos de monitoria também permanecem no modelo conceitual do banco, sem implementação nesta versão.

## 💾 Estrutura do Banco de Dados

O modelo e o dicionário de dados estão em [`docs/banco_dados.md`](docs/banco_dados.md). A aplicação registra atualmente as tabelas de usuários, espaços (incluindo horários, pausas e vínculos) e projetos (incluindo participantes). O restante do diagrama descreve o modelo conceitual de funcionalidades futuras.

## 🛠️ Como Executar o Projeto Localmente

### Pré-requisitos

* Python 3.11+

* Docker e Docker Compose (Para o banco de dados)

### Passos

1. **Clone o repositório:**

   ```
   git clone https://github.com/GlinsC/Projeto_AgendamentoLAB.git
   cd Projeto_AgendamentoLAB
   
   ```

2. **Crie e ative um ambiente virtual:**

   ```
   python -m venv .venv
   # Linux/Mac
   source .venv/bin/activate
   # Windows
   .venv\Scripts\Activate.ps1
   
   ```

3. **Instale as dependências:**

   ```
   pip install -r requirements.txt
   
   ```

4. **Inicie o Banco de Dados com Docker:**

   ```
   docker-compose up -d db
   
   ```

5. **Configure as Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz do projeto com as configurações do banco e a chave JWT:

   ```env
   URL_BANCO_DADOS=postgresql+psycopg://colab_user:colab_password@localhost:5432/colab_db
   CHAVE_SECRETA=defina-uma-chave-segura
   MINUTOS_EXPIRACAO_TOKEN=30
   ORIGENS_CORS=*
   HOSTS_PERMITIDOS=localhost,127.0.0.1
   PERMITE_CREDENCIAIS_CORS=false
   ```

   `ORIGENS_CORS` recebe origens completas, separadas por vírgula (por exemplo, `http://localhost:5173`). `*` permite qualquer origem e não pode ser combinado com credenciais CORS. `HOSTS_PERMITIDOS` recebe apenas hosts, sem esquema ou porta.

6. **Crie as tabelas iniciais:**
   Ao iniciar, a aplicação cria as tabelas de usuários, espaços e projetos caso ainda não existam. O versionamento e as alterações do esquema do banco devem seguir o fluxo de migração adotado pelo projeto.

7. **Inicie o Servidor Local:**

   ```
   uvicorn main:app --reload
   
   ```

## 📐 Padrões de Código e Convenções

Para manter a consistência, legibilidade e o alinhamento com as regras de negócio do laboratório, a base de código adota o conceito de **Linguagem Ubíqua**. Isso significa que o código deve refletir os mesmos termos usados pelos usuários no dia a dia do COLAB. 

Por isso, adotamos as seguintes diretrizes e padrões de nomenclatura:

* **Idioma Base:** Todo o código-fonte (variáveis, funções, classes, arquivos e comentários) é escrito em **Português**. Termos técnicos globais de frameworks (como `id`, `payload`, `router` ou `status_code`) podem ser mantidos no idioma original caso sejam exigências da linguagem.
* **Classes, Modelos e Exceções:** Seguem o padrão `PascalCase`.
  * *Exemplos:* `EntidadeBase`, `UsuarioLogin`, `RegraDeNegocioErro`, `SessaoLocal`.
* **Variáveis, Atributos e Funções/Métodos:** Seguem o padrão `snake_case` (conforme PEP 8 do Python).
  * *Exemplos:* `nome_completo`, `vinculo_institucional`, `pegar_banco_dados()`.
* **Constantes e Configurações Globais:** Seguem o padrão `UPPER_SNAKE_CASE`.
  * *Exemplos:* `TEMPO_EXPIRACAO_TOKEN`, `LIMITE_DIAS_AGENDAMENTO`.
* **Arquivos e Pastas:** Seguem o padrão `snake_case`.
  * *Exemplos:* `entidade_base.py`, `casos_de_uso/`, `compartilhado/`.
* **Tipagem Estática:** O uso de *Type Hints* (tipagem) é **obrigatório** em todas as funções e métodos para garantir previsibilidade e integração perfeita com a validação do FastAPI/Pydantic.

### 📚 Documentação da API

Com a aplicação em execução, acesse a documentação interativa nativa do FastAPI gerada automaticamente pelo Swagger UI:

* **Swagger UI:** `http://localhost:8000/docs`

* **ReDoc:** `http://localhost:8000/redoc`

## 👥 Equipe do Projeto

Projeto desenvolvido pelos alunos do Bacharelado em Sistemas de Informação - IFAL Campus Maceió:

* João Vinícius Rocha Costa

* Jorge Matheus

* Nicolas Andrey

* Gabriel Lins

* Davidson Rogério de Aguiar

* Marlos Cesar

**Orientador:** Prof. Edison Camilo de Moraes Junior

*Maceió/AL - Setembro de 2026*