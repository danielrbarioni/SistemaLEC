## ADDED Requirements

### Requirement: Isolamento do banco de dados SQLite de produção

O sistema MUST isolar completamente o arquivo de banco de dados SQLite (`data/app.db`) do versionamento do Git e das rotinas de deploy, garantindo que atualizações de código na VM não sobrescrevam ou apaguem dados de produção.

#### Scenario: Ignorar arquivos de banco SQLite no repositório Git
- **WHEN** o desenvolvedor executa `git status` ou faz commit no repositório local
- **THEN** os arquivos `app.db`, `data/app.db` e qualquer arquivo `.db` MUST ser ignorados pelo Git e NUNCA ser incluídos nos commits ou no repositório remoto.

#### Scenario: Deploy de código na VM sem sobrescrita da base de dados
- **WHEN** o script de deploy atualiza o código na VM executando atualizações pelo Git (ex: `git fetch` e atualizações de código)
- **THEN** o arquivo de banco de dados SQLite `/var/app/sistemalec/data/app.db` na VM MUST permanecer intocado e os dados de usuários e histórico preservados.

#### Scenario: Unificação da localização do banco de dados SQLite
- **WHEN** a aplicação FastAPI é iniciada localmente ou em produção na VM
- **THEN** a aplicação MUST utilizar unicamente a variável de ambiente apontando para `data/app.db`, eliminando caminhos ambíguos ou bancos duplicados na raiz do projeto.
