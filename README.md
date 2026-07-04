# SisCAM — Sistema de Controle de Acesso Militar

O **SisCAM** é uma aplicação desktop de nível corporativo projetada para centralizar, monitorar e auditar o fluxo de pessoal (militares) e material (viaturas operacionais, administrativas ou veículos particulares) em Organizações Militares (OM). 

O sistema foi desenvolvido utilizando uma arquitetura robusta e moderna em Python, garantindo integridade dos dados, isolamento de regras de negócio, testes automatizados e tolerância a falhas para operação contínua em guaritas e portarias.

---

## 🛠️ Tecnologias e Arquitetura

O projeto adota padrões de design de software de mercado para manter o código limpo, testável e de fácil manutenção:

*   **Interface Gráfica (GUI):** `PySide6` (Qt para Python) — Utilização de layouts nativos fluidos, controle estruturado de abas (`QTabWidget`), modais dinâmicos (`QDialog`) e tabelas responsivas (`QTableWidget`).
*   **Persistência de Dados e ORM:** `SQLAlchemy` — Mapeamento Objeto-Relacional (ORM) modular. O sistema se comunica apenas com modelos de domínio, tornando a aplicação **independente de banco de dados**.
*   **Banco de Dados Padrão:** `SQLite` — Armazenamento local leve em arquivo único (`siscam.db`), ideal para operação descentralizada.
*   **Camada de Negócio (Domain Services):** Isolamento completo das regras de controle de acesso (ex: validação de tipo de entrada, incremento/decremento automático do efetivo da OM no dashboard) fora das telas da interface.
*   **Qualidade e Testes:** `pytest` — Suíte de testes automatizados com injeção de banco de dados volátil em memória (`sqlite:///:memory:`).
*   **Segurança e Resiliência:** Interceptador global de exceções (`GlobalExceptionHandler`) com persistência automática de rastreamento de falhas na tabela `LogSistema`, blindando o executável contra fechamentos abruptos (crashes).

## Estrutura de pastas (comentada)

```
.
├── init_db.py                # Script de criação/população inicial do banco local
├── main.py                   # Ponto de entrada da aplicação (inicializa UI e serviços)
├── requirements.txt          # Dependências do projeto
├── app/                      # Código-fonte principal
│   ├── core/                 # Utilitários centrais (ex.: segurança, configuração global)
│   │   └── security.py       # Funções de hashing, gerenciamento de senhas e políticas
│   ├── database/             # Conexão e configuração do banco de dados
│   │   └── connection.py     # Fornece a `engine` e `SessionLocal` (string de conexão aqui)
│   ├── models/               # Modelos de domínio (SQLAlchemy)
│   │   └── models.py         # Declara as entidades/tabelas (Militar, Viatura, Log, Usuario...)
│   ├── repositories/         # Acesso a dados (abstração do ORM)
│   │   └── usuario_repository.py  # CRUD e consultas específicas para usuários
│   ├── services/             # Regras de negócio / serviços de domínio
│   │   ├── acesso_service.py      # Regras para registrar entradas/saídas
│   │   ├── auth_service.py        # Autenticação, verificação de credenciais, tokens
│   │   ├── om_service.py          # Estado e contagem de efetivo da OM
│   │   └── portaria_service.py    # Lógica crítica da portaria (validações, fluxos)
│   ├── utils/                # Utilitários e helpers reutilizáveis
│   │   └── exception_handler.py  # Interceptador global de exceções e persistência de logs
│   └── views/                # Camada de apresentação (PySide6)
│       ├── login_view.py         # Tela de autenticação de operadores
│       ├── main_view.py          # Dashboard principal e fluxo de portaria
│       ├── management_view.py    # Painel administrativo (buscas, relatórios)
│       ├── militar_dialog.py     # Diálogo para cadastro/edição de militares
│       ├── viatura_dialog.py     # Diálogo para cadastro/edição de viaturas
│       └── components/           # Componentes UI reutilizáveis
│           └── __init__.py
├── tests/                    # Testes automatizados
│   ├── conftest.py           # Fixtures (ex.: engine em memória, sessão de teste)
│   └── test_portaria.py      # Testes unitários das regras de portaria
└── README.md                 # (este arquivo)
```

---

## Arquivos cruciais — descrição detalhada

- `main.py`:
  - Inicializa configuração global, conecta ao banco (via `app/database/connection.py`), instancia serviços e abre a interface PySide6.
  - Ponto onde se deve tratar argumentos de linha de comando (modo debug, usar DB alternativo, etc.).

- `init_db.py`:
  - Script responsável por criar o esquema (chamar `models.Base.metadata.create_all(engine)`) e popular dados essenciais (usuários admin, OM padrão).
  - Útil para primeira implantação e para regenerar o banco local em desenvolvimento.

- `requirements.txt`:
  - Lista as dependências do projeto (ex.: PySide6, SQLAlchemy, pytest). Atualize quando adicionar libs.

- `app/database/connection.py`:
  - Centraliza a string de conexão e a criação do `engine` e `SessionLocal`.
  - Para testes, altere para `sqlite:///:memory:` ou forneça via variável de ambiente.

- `app/models/models.py`:
  - Define as classes do domínio mapeadas pelo SQLAlchemy (ex.: `Militar`, `Viatura`, `Usuario`, `LogSistema`, `Acesso`).
  - Qualquer alteração no modelo requer migração do esquema ou recriação do DB para desenvolvimento.

- `app/repositories/usuario_repository.py`:
  - Encapsula consultas e operações de CRUD de `Usuario`. Usado por `auth_service.py` e pela UI administrativa.
  - Repositórios mantêm a dependência do ORM isolada dos serviços.

- `app/services/auth_service.py`:
  - Valida credenciais, utiliza `app/core/security.py` para hashing/verificação de senha.
  - Pode emitir tokens ou manter sessão de usuário para a UI.

- `app/services/portaria_service.py`:
  - Contém validações críticas: permissões de entrada, checagens de pendências, regras de movimentação de viaturas.
  - Coberto por testes em `tests/test_portaria.py`.

- `app/services/acesso_service.py` (ou `acesso_service.py`):
  - Serviço específico para gravar eventos de acesso (timestamp, usuário operador, alvo do acesso).
  - Gera entradas na tabela de auditoria para rastreabilidade.

- `app/services/om_service.py`:
  - Gerencia estado agregado da Organização Militar (ex.: contagem de efetivo presente) e atualiza dashboards.

- `app/utils/exception_handler.py`:
  - Captura exceções não tratadas, grava `LogSistema` e, quando possível, mostra diálogo amigável na UI.
  - Essencial para resiliência em operação em guarnições.

- `app/core/security.py`:
  - Implementa políticas de senha, hashing (bcrypt/argon2), e funções auxiliares (verificar força de senha, gerar salts).

- `app/views/*.py` (UI):
  - `login_view.py`: Solicita credenciais e chama `auth_service`.
  - `main_view.py`: Exibe dashboard (contadores, filtros) e interface de controle de entradas/saídas.
  - `management_view.py`: Ferramentas administrativas (busca, relatórios, manutenção de dados).
  - `militar_dialog.py` / `viatura_dialog.py`: Formulários modais para cadastro/edição.
  - As views devem ser leves — delegar lógica para `services` e chamadas a `repositories`.

- `tests/conftest.py`:
  - Configura fixture do SQLAlchemy com `engine` em memória e `Session` isolada para testes.
  - Deve garantir rollback entre testes e prover dados de exemplo.

- `tests/test_portaria.py`:
  - Testes unitários das regras de portaria contidas em `portaria_service.py`.
  - Executar com `pytest` para verificar integridade das regras implementadas.

---

## Como rodar (resumo rápido)

1. Criar e ativar venv:

```bash
python -m venv .venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Inicializar banco local (gera `siscam.db`):

```bash
python init_db.py
```

3. Rodar aplicação:

```bash
python main.py
```

4. Executar testes:

```bash
pytest -q
```

--
