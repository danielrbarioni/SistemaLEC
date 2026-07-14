## Why

Precisamos cadastrar o usuário administrador `daniel.barioni` (nome completo Daniel Barioni) no banco de dados local SQLite (tabela `usuarios`) associado ao perfil `ADMIN`. Isso permitirá que esse usuário se autentique (via AD/Mock) e acesse o sistema com privilégios de administrador.

## What Changes

- Criação de um script de semente/migração (seed script) para inserir o usuário `daniel.barioni` com perfil `ADMIN` na tabela `usuarios` do banco de dados local (`data/app.db`).
- Execução do script para persistir o novo usuário.

## Capabilities

### New Capabilities
- `admin-seed`: Cadastro/seeding do usuário administrador `daniel.barioni` no banco de dados SQLite local.

### Modified Capabilities

## Impact

- Afeta a tabela `usuarios` no banco de dados SQLite local (`data/app.db`), inserindo uma nova linha.
