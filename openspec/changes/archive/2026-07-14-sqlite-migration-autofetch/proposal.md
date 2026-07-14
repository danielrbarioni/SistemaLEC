## Why

O sistema atual depende de arquivos CSV estáticos (`data/pacientes.csv`, `data/solicitacoes.csv` e `data/status_locais.csv`) para o armazenamento de dados. Isso limita operações simultâneas, carece de integridade estrutural e torna ineficiente a busca de dados em tempo real (como buscar nomes de pacientes por prontuário). A migração para SQLite possibilita consultas estruturadas, criação automática de tabelas e recuperação imediata dos dados dos pacientes.

## What Changes

- **Migração do Banco de Dados**: Migrar o acesso a dados no backend de arquivos CSV para um banco de dados SQLite local (`data/app.db`).
- **Autopreenchimento de Dados**: Ao digitar o prontuário no formulário do frontend, o sistema consulta o backend (AGHU/PostgreSQL ou SQLite) e autopreenche o nome completo do paciente.
- **Tabelas Persistentes**: Criação automática das tabelas SQLite para `pacientes`, `solicitacoes` e `status_locais` na inicialização do sistema.
- **Migração de Dados**: Script utilitário para importar os registros existentes nos arquivos CSV para o novo banco SQLite.

## Capabilities

### New Capabilities
- `patient-autofetch`: Recuperar dados demográficos do paciente pelo número do prontuário sob demanda.

### Modified Capabilities
- `paciente`: Alterar o provedor de dados para consultar o AGHU/PostgreSQL (principal) ou o SQLite local (fallback) em vez de ler arquivo CSV.
- `solicitacao`: Alterar o provedor de dados para ler/gravar solicitações no SQLite em vez de arquivo CSV.

## Impact

- **Backend**: Fábricas de dependência do FastAPI, gerenciamento de conexões no lifespan e rotas de consulta.
- **Frontend**: Requisições de API no painel de solicitações para obter dados do prontuário e preencher campos automaticamente.
- **Dependências**: SQLite e drivers assíncronos (`aiosqlite`).
