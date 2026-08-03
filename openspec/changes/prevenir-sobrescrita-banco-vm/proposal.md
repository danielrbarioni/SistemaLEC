## Why

Ao realizar deploys do ambiente local para a VM, os arquivos de banco de dados SQLite (`app.db` e `data/app.db`) estavam sendo rastreados pelo Git no repositório. Durante o deploy na VM, o comando `git reset --hard origin/main` ou a sincronização de arquivos substituía o banco de dados da VM (contendo usuários recém-cadastrados em produção e alterações no histórico) pela versão defasada do banco armazenada no Git.

Esta alteração é necessária para garantir a persistência dos dados de produção na VM, eliminar o rastreamento de bancos SQLite pelo Git, unificar a referência do banco de dados e proteger a base de dados contra sobrescritas em deploys futuros.

## What Changes

- **Remoção de Bancos de Dados do Rastreamento Git**: Remover `app.db` e `data/app.db` do Git index (`git rm --cached`).
- **Atualização do `.gitignore`**: Adicionar regras para ignorar `*.db`, `app.db` e `data/*.db` (mantendo apenas scripts de migração/estrutura como `.gitkeep` ou `alembic`).
- **Unificação da Configuração de Banco**: Garantir que tanto localmente quanto na VM o caminho do SQLite seja unicamente `data/app.db` (eliminando cópias duplicadas na raiz).
- **Ajuste nos Scripts de Deploy**: Modificar scripts como `scratch/deploy_code_to_vm.py` para nunca realizar limpeza ou reset que afete o arquivo `/var/app/sistemalec/data/app.db`.
- **Preservação e Restauração de Dados da VM**: Criar procedimento de salvaguarda dos usuários cadastrados na VM e integridade do histórico.

## Capabilities

### New Capabilities
- `vm-db-protection`: Mecanismo e regras de configuração para garantir que a base de dados SQLite da VM seja persistente, isolada do versionamento Git e protegida durante atualizações de código.

### Modified Capabilities

## Impact

- **Repositório Git**: Remoção dos arquivos `.db` do repositório remoto e local.
- **Deploy de VM**: `scratch/deploy_code_to_vm.py` e execuções remota via SSH.
- **Configuração `.env`**: Consistência das variáveis `APP_DB_URL` e `SQLITE_DSN`.
- **Integridade de Dados**: Preservação contínua de usuários e solicitações em ambiente de homologação/produção.
