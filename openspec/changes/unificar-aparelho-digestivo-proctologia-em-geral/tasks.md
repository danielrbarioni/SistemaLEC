# Tasks

## 1. Unificação no Backend e Migração do Banco de Dados

- [x] 1.1 Atualizar `normalize_specialty_name` em `src/helpers/string_helper.py` para converter `APARELHO DIGESTIVO`, `APARELHO_DIGESTIVO`, `CIRURGIA DO APARELHO DIGESTIVO` e `PROCTOLOGIA` em `GERAL`, verificando com asserções em Python.
- [x] 1.2 Atualizar `migrate_cirurgia_geral_to_geral` em `src/helpers/database_migration_helper.py` para migrar perfis, usuários, pacientes, solicitações, categorizações profissionais e solicitações de criação de usuário de `Aparelho Digestivo` e `Proctologia` para `GERAL` e remover os perfis extintos, verificando com teste em banco SQLite.

## 2. Atualização do Frontend e Deploy na VM

- [x] 2.1 Remover `'APARELHO DIGESTIVO'` e `'PROCTOLOGIA'` de `ESPECIALIDADE_AGHU_MAP` em `frontend/src/utils/especialidadeAghuMap.ts` (mantendo `'GERAL': [33]`) e atualizar `normalizeEsp` em `DefaultLayout.vue`, `InteracoesLec.vue`, `Pacientes.vue`, `Historico.vue` e `Perfis.vue`.
- [x] 2.2 Compilar o frontend (`npm run build`), realizar o deploy na VM (`scripts/deploy_to_vm.py` com backup automático prévio do `app.db`) e verificar no banco da VM que os perfis `Aparelho Digestivo` e `Proctologia` deixaram de existir e seus registros foram unificados em `GERAL`.
